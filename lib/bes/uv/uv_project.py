#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import json
from os import path

from bes.common.object_util import object_util
from bes.files.bf_filename import bf_filename
from bes.files.bf_file_ops import bf_file_ops
from bes.files.checksum.bf_checksum import bf_checksum
from bes.property.cached_property import cached_property
from bes.script.blurb import blurb
from bes.system.check import check
from bes.system.env_var import env_var
from bes.system.execute import execute
from bes.system.host import host
from bes.system.log import logger
from bes.system.os_env import os_env

from . import uv_error
from . import uv_project_options as uv_project_options_module
from . import uv_venv as uv_venv_module

class uv_project(object):
  'High-level uv virtual environment and package management.'

  _log = logger('uv_project')

  _installed_package = namedtuple('_installed_package', 'name, version')
  _outdated_package = namedtuple('_outdated_package', 'name, current_version, latest_version')

  def __init__(self, options=None):
    check.check_uv_project_options(options)

    self._options = options or uv_project_options_module.uv_project_options()
    self._root_dir = self._options.resolve_root_dir()
    self._uv_exe_path = self._options.resolve_uv_exe()
    self._venv = uv_venv_module.uv_venv(self._root_dir,
                                         self._uv_exe_path,
                                         python=self._options.python)

  @property
  def options(self):
    return self._options

  @property
  def root_dir(self):
    return self._root_dir

  def ensure_ready(self):
    'Create the virtual environment if it does not already exist.'
    self._venv.create()

  def install(self, package_name, version=None):
    'Install a package with optional version.'
    check.check_string(package_name)
    check.check_string(version, allow_none=True)

    if version:
      spec = f'{package_name}=={version}'
    else:
      spec = package_name
    self._log.log_d(f'install: {spec}')
    args = ['pip', 'install', spec]
    rv = self.call_uv(args, raise_error=False)
    if rv.exit_code != 0:
      raise uv_error.uv_error(f'Failed to install "{spec}": {rv.stdout}')

  def install_requirements(self, requirements_files):
    'Install packages from one or more requirements files.'
    requirements_files = object_util.listify(requirements_files)
    check.check_string_seq(requirements_files)

    for requirements_file in requirements_files:
      if not path.exists(requirements_file):
        raise uv_error.uv_error(f'Requirements file not found: "{requirements_file}"')
    for requirements_file in requirements_files:
      self._install_one_requirements_file(requirements_file)

  def _install_one_requirements_file(self, requirements_file):
    new_checksum = bf_checksum.checksum(requirements_file, 'sha256')
    checksum_file = self._requirements_checksum_file(requirements_file)
    if path.exists(checksum_file):
      old_checksum = bf_file_ops.read(checksum_file, encoding='utf-8').strip()
      if old_checksum == new_checksum:
        self._log.log_d(f'{requirements_file}: checksum unchanged, skipping install')
        return
    args = ['pip', 'install', '-r', requirements_file]
    rv = self.call_uv(args, raise_error=False)
    if rv.exit_code != 0:
      raise uv_error.uv_error(f'Failed to install requirements "{requirements_file}": {rv.stdout}')
    bf_file_ops.save(checksum_file, content=new_checksum)

  def _requirements_checksum_file(self, requirements_file):
    assert path.isabs(requirements_file)
    basename = path.basename(requirements_file)
    return path.join(self._root_dir, '.uv_cache', 'requirements_checksums', basename)

  def installed(self):
    'Return a list of installed packages.'
    args = ['pip', 'list', '--format', 'json']
    rv = self.call_uv(args, raise_error=True, stderr_to_stdout=False)
    packages = json.loads(rv.stdout)
    result = [self._installed_package(p['name'].lower(), p['version']) for p in packages]
    return sorted(result, key=lambda item: item.name)

  def outdated(self):
    'Return a list of outdated packages.'
    args = ['pip', 'list', '--outdated', '--format', 'json']
    rv = self.call_uv(args, raise_error=True, stderr_to_stdout=False)
    packages = json.loads(rv.stdout)
    return [self._outdated_package(p['name'].lower(), p['version'], p['latest_version'])
            for p in packages]

  def upgrade(self, packages):
    'Upgrade one or more packages to their latest versions.'
    packages = object_util.listify(packages)
    check.check_string_seq(packages)

    args = ['pip', 'install', '--upgrade'] + list(packages)
    rv = self.call_uv(args, raise_error=False)
    if rv.exit_code != 0:
      raise uv_error.uv_error(f'Failed to upgrade {packages}: {rv.stdout}')

  def needs_upgrade(self, package_name):
    'Return True if package_name has a newer version available.'
    check.check_string(package_name)

    for item in self.outdated():
      if item.name == package_name.lower():
        return True
    return False

  def version(self, package_name):
    'Return the installed version of package_name.'
    check.check_string(package_name)

    for item in self.installed():
      if item.name == package_name.lower():
        return item.version
    raise uv_error.uv_error(f'Package not found: "{package_name}"')

  def call_uv(self, args, raise_error=True, stderr_to_stdout=True):
    'Run a uv subcommand inside the virtual environment.'
    command = [self._uv_exe_path] + list(args)
    self._log.log_d(f'call_uv: {command}')
    return execute.execute(command,
                           env=self.env,
                           raise_error=raise_error,
                           stderr_to_stdout=stderr_to_stdout,
                           check_python_script=False)

  def call_program(self, args, extra_env=None):
    'Run a program inside the virtual environment.'
    check.check_string_seq(args, allow_none=False)

    run_env = os_env.clone_current_env()
    run_env.update(self.env)
    if extra_env:
      check.check_dict(extra_env)
      run_env.update(extra_env)
    self._log.log_d(f'call_program: {args}')
    return execute.execute(list(args),
                           env=run_env,
                           raise_error=True,
                           check_python_script=False)

  def program_path(self, program):
    'Return the absolute path to a binary in the venv.'
    check.check_string(program)

    if host.is_windows():
      if not bf_filename.has_extension(program, 'exe', ignore_case=True):
        program = bf_filename.add_extension(program, 'exe')
    return path.join(self._venv.bin_dir, program)

  def has_program(self, program):
    'Return True if the venv contains program.'
    check.check_string(program)

    return path.isfile(self.program_path(program))

  @property
  def PYTHONPATH(self):
    return [self._venv.site_packages_dir]

  @property
  def env(self):
    'Minimal environment dict for subprocess calls within the venv.'
    environment = os_env.make_clean_env()
    env_var(environment, 'VIRTUAL_ENV').value = self._venv.root_dir
    env_var(environment, 'PATH').prepend(self._venv.bin_dir)
    if self._options.uv_cache_dir:
      env_var(environment, 'UV_CACHE_DIR').value = self._options.uv_cache_dir
    return environment
