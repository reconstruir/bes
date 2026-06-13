#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.algorithm import algorithm
from bes.files.bf_dir import bf_dir
from bes.files.bf_file_ops import bf_file_ops
from bes.files.bf_check import bf_check
from bes.property.cached_property import cached_property
from bes.system.check import check
from bes.system.execute import execute
from bes.system.host import host
from bes.system.log import logger
from bes.uv.uv_exe import uv_exe
from bes.uv.uv_project import uv_project
from bes.uv.uv_project_options import uv_project_options
from bes.uv_installer.uv_installer import uv_installer
from bes.uv_installer.uv_installer_options import uv_installer_options
from bes.version.semantic_version import semantic_version

from .bes_project_error import bes_project_error
from .bes_project_options import bes_project_options

class bes_project(object):
  'Bes project — manages uv venvs for one named project across multiple Python versions.'

  _log = logger('bes_project')

  def __init__(self, options=None):
    check.check_bes_project_options(options, allow_none=True)

    self._options = options or bes_project_options()
    self._root_dir = self._options.resolve_root_dir()
    self._uv_install_dir = path.join(self._root_dir, '.uv_install')
    self._uv_cache_dir = path.join(self._root_dir, '.uv_cache')
    self._project_base_dir = self._make_project_base_dir()

  def _make_project_base_dir(self):
    if self._options.name:
      return path.join(self._root_dir, 'projects', self._options.name)
    return path.join(self._root_dir, 'projects', 'default')

  @cached_property
  def _uv_exe_path(self):
    # explicit path wins
    if self._options.uv_exe:
      return uv_exe.find(self._options.uv_exe)
    # system uv (UV env var, ~/.local/bin/uv, shutil.which)
    candidate = uv_exe.find_or_none()
    if candidate:
      return candidate
    # already installed in this root from a previous run
    local_candidate = path.join(self._uv_install_dir, 'uv.exe' if host.is_windows() else 'uv')
    if path.isfile(local_candidate):
      return local_candidate
    # install uv into the shared root
    self._log.log_d(f'_uv_exe_path: uv not found, installing into {self._uv_install_dir}')
    installer_options = uv_installer_options(install_dir=self._uv_install_dir,
                                              verbose=self._options.verbose)
    uv_installer(installer_options).install()
    return uv_exe.find(local_candidate)

  def _dir_for_version(self, version):
    return path.join(self._project_base_dir, version)

  def _make_uv_project(self, version):
    options = uv_project_options(root_dir=self._dir_for_version(version),
                                  uv_exe=self._uv_exe_path,
                                  python=version,
                                  uv_cache_dir=self._uv_cache_dir,
                                  verbose=self._options.verbose,
                                  debug=self._options.debug)
    return uv_project(options)

  def ensure(self, versions, requirements, requirements_dev=None):
    'Ensure venvs exist and requirements are installed for the given Python versions.'
    check.check_string_seq(versions)

    old_versions = set(self.versions)
    resolved = self._resolve_versions(versions)
    to_remove = old_versions - set(resolved)

    requirements = bf_check.check_file(requirements)
    requirements_dev = bf_check.check_file(requirements_dev, allow_none=True)

    for version in resolved:
      proj = self._make_uv_project(version)
      proj.ensure_ready()
      proj.install_requirements(requirements)
      if requirements_dev:
        proj.install_requirements(requirements_dev)

    for version in to_remove:
      self._remove_dir(version)

  def _remove_dir(self, version):
    p = self._dir_for_version(version)
    if path.exists(p):
      bf_file_ops.remove(p)

  @property
  def versions(self):
    'Return the Python versions on disk for this project.'
    if not path.exists(self._project_base_dir):
      return []
    dirs = bf_dir.list(self._project_base_dir, relative=True)
    return semantic_version.sort_string_list(dirs)

  def activate_script(self, version, variant=None):
    'Return the path to the activate script for the given version.'
    check.check_string(version)
    check.check_string(variant, allow_none=True)

    proj = self._make_uv_project(version)
    return proj._venv.activate_script(variant=variant)

  def _list_uv_python_versions(self):
    'Return unique sorted major.minor version strings installed per uv python list.'
    command = [self._uv_exe_path, 'python', 'list', '--only-installed']
    rv = execute.execute(command, raise_error=False, stderr_to_stdout=False,
                         check_python_script=False)
    if rv.exit_code != 0:
      return []
    seen = set()
    result = []
    for line in rv.stdout.splitlines():
      parts = line.split()
      if not parts:
        continue
      spec = parts[0]  # e.g. 'cpython-3.13.13-macos-aarch64-none'
      if not spec.startswith('cpython-'):
        continue
      version_full = spec.split('-')[1]  # '3.13.13'
      if '+' in version_full:
        continue  # skip freethreaded variants
      ver_parts = version_full.split('.')
      if len(ver_parts) < 2:
        continue
      major_minor = f'{ver_parts[0]}.{ver_parts[1]}'
      if major_minor not in seen:
        seen.add(major_minor)
        result.append(major_minor)
    return result

  def _resolve_versions(self, versions):
    result = []
    if not versions:
      installed = self._list_uv_python_versions()
      result = [installed[0]] if installed else []
    else:
      flat = self._flatten_versions(versions)
      for v in flat:
        result.extend(self._resolve_one_version(v))
    return algorithm.unique(result)

  def _resolve_one_version(self, python_version):
    if python_version in ('all', 'all3', 'all2', 'all23', 'latest'):
      installed = self._list_uv_python_versions()
      if python_version in ('all', 'all3'):
        return [v for v in installed if v.startswith('3.')]
      elif python_version == 'all2':
        return [v for v in installed if v.startswith('2.')]
      elif python_version == 'all23':
        return installed
      elif python_version == 'latest':
        return [installed[0]] if installed else []
    return [python_version]

  def _flatten_versions(self, versions):
    result = []
    for v in versions:
      result.extend([pv.lower().strip() for pv in str(v).split(',')])
    return algorithm.unique(result)
