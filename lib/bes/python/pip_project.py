#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import copy
import json
import os
from os import path
import pprint

from ..system.check import check
from bes.common.object_util import object_util
from bes.common.hash_util import hash_util
from bes.fs.dir_util import dir_util
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.fs.filename_util import filename_util
from bes.property.cached_property import cached_property
from bes.system.command_line import command_line
from bes.system.env_var import env_var
from bes.system.execute import execute
from bes.system.host import host
from bes.system.log import logger
from bes.system.os_env import os_env
from bes.url.url_util import url_util

from .pip_error import pip_error
from .pip_exe import pip_exe
from .pip_project_options import pip_project_options
from .python_error import python_error
from .python_installation import python_installation
from .python_source import python_source
from .python_version import python_version
from .python_virtual_env import python_virtual_env

class pip_project(object):
  'Pip project.'

  _log = logger('pip_project')
  
  def __init__(self, options = None):
    check.check_pip_project_options(options)

    self._extra_env = {}
    self._options = options or check_pip_project_options()
    self._log.log_d(f'__init__: options={options}')
    self._root_dir = self._options.resolve_root_dir()
    self._pip_cache_dir = path.join(self.droppings_dir, 'pip-cache')
    self._fake_home_dir = path.join(self.droppings_dir, 'fake-home')
    file_util.mkdir(self._fake_home_dir)
    self._fake_tmp_dir = path.join(self.droppings_dir, 'fake-tmp')
    file_util.mkdir(self._fake_tmp_dir)

    self._common_pip_args = [
      '--cache-dir', self._pip_cache_dir,
    ]
    try:
      self._do_init(1)
    except python_error as ex:
      if 'version mismatch' in ex.message:
        self._options.blurber.blurb('{} - Fixing automagically.'.format(ex.message))
        self._options.blurber.blurb('removing {}'.format(self._root_dir))
        file_util.remove(self._root_dir)
        self._do_init(2)

  def _do_init(self, attempt_number):
    self._log.log_d('_do_init:{}: pip_exe={} pip_env={} project_dir={}'.format(attempt_number,
                                                                               self.pip_exe,
                                                                               self.env,
                                                                               self.root_dir))
    self._reinstall_pip_if_needed()
    self._ensure_basic_packages()

  def _reinstall_pip_if_needed(self):
    'On linux there are problem with old python versions that get fixed by forcing a reinstall of pip'
    if not host.is_linux():
      return
    args = [
      'install',
      '--ignore-installed',
      'pip',
    ]
    rv = self.call_pip(args)

  def _ensure_basic_packages(self):
    'Ensure that some basic python packages are installed.'
    installed = set([ item.name for item in self.installed() ])
    if not 'wheel' in installed:
      self.install('wheel')
    if not 'setuptools' in installed:
      self.install('setuptools')

  @cached_property
  def _original_python_exe(self):
    return self._options.resolve_python_exe()
    
  @cached_property
  def virtual_env(self):
    self._log.log_d(f'_original_python_exe={self._original_python_exe}')
    return python_virtual_env(self._original_python_exe, self.root_dir)

  @cached_property
  def installation(self):
    return self.virtual_env.installation

  @cached_property
  def python_exe(self):
    return self.installation.python_exe
  
  @cached_property
  def root_dir(self):
    return self._root_dir

  @cached_property
  def droppings_dir(self):
    return path.join(self.root_dir, '.droppings')
    
  @cached_property
  def user_base_install_dir(self):
#    if host.is_windows():
#      user_base_install_dir = path.join(self.root_dir, self.installation.windows_versioned_install_dirname)
#    elif host.is_unix():
#      user_base_install_dir = self.root_dir
#    else:
#      host.raise_unsupported_system()
#    user_base_install_dir = self.root_dir
#    return user_base_install_dir
    return self.root_dir
  
  @cached_property
  def bin_dir(self):
    if host.is_windows():
      bin_dir = path.join(self.user_base_install_dir, 'Scripts')
    elif host.is_unix():
      bin_dir = path.join(self.user_base_install_dir, 'bin')
    else:
      host.raise_unsupported_system()
    return bin_dir
  
  @cached_property
  def site_packages_dir(self):
    if host.is_windows():
      site_packages_dir = path.join(self.user_base_install_dir, 'site-packages')
    elif host.is_unix():
      site_packages_dir = path.join(self.user_base_install_dir, 'lib/python/site-packages')
    else:
      host.raise_unsupported_system()
    return site_packages_dir
  
  @property
  def env(self):
    'Make a clean environment for python or pip'
    clean_env = os_env.make_clean_env()
    env_var(clean_env, 'PYTHONUSERBASE').value = self.root_dir
    env_var(clean_env, 'PYTHONPATH').path = self.PYTHONPATH
    env_var(clean_env, 'PATH').prepend(self.PATH)
    env_var(clean_env, 'HOME').value = self._fake_home_dir
    env_var(clean_env, 'TMPDIR').value = self._fake_tmp_dir
    env_var(clean_env, 'TMP').value = self._fake_tmp_dir
    env_var(clean_env, 'TEMP').value = self._fake_tmp_dir
    clean_env.update(self._extra_env)
    return clean_env

  @cached_property
  def PYTHONPATH(self):
    return self.installation.PYTHONPATH + [
      self.site_packages_dir,
    ]

  @cached_property
  def PATH(self):
    return [
      path.dirname(self.python_exe),
      self.bin_dir,
    ] + self.installation.PATH
  
  @cached_property
  def python_exe(self):
    return self.installation.python_exe

  @cached_property
  def pip_exe(self):
    return self.installation.pip_exe

  def activate_script(self, variant = None):
    'Return the activate script for the virtual env'
    return python_source.activate_script(self.root_dir, variant)
  
  @property
  def pip_version(self):
    return pip_exe.version(self.pip_exe)
  
  def pip_is_installed(self):
    'Return True if pip is installed'
    return self.pip_exe and path.exists(self.pip_exe)

  def check_pip_is_installed(self):
    'Check that pip is installed and if not raise an error'
    if not self.pip_is_installed():
      raise pip_error('Pip not found: {}'.format(self.pip_exe or ''))

  _outdated_package = namedtuple('_outdated_package', 'name, current_version, latest_version, latest_filetype')
  def outdated(self):
    'Return a list of outdated packages'
    args = [
      'list',
      '--outdated',
      '--format', 'json',
      '--disable-pip-version-check',
    ]
    rv = self.call_pip(args, stderr_to_stdout = False)
    outdated = json.loads(rv.stdout)

    result = []
    for next_item in outdated:
      op = self._outdated_package(next_item['name'].lower(),
                                  next_item['version'],
                                  next_item['latest_version'],
                                  next_item['latest_filetype'])
      result.append(op)
    self._log.log_d('outdated: outdated={}'.format(pprint.pformat(result)))
    return result

  _installed_package = namedtuple('_installed_package', 'name, version')
  def installed(self):
    'Return a list of installed packages'
    args = [
      'list',
      '--format', 'json',
      '--disable-pip-version-check',
    ]
    rv = self.call_pip(args, stderr_to_stdout = False)
    installed = json.loads(rv.stdout)
    self._log.log_d('installed: installed={}'.format(pprint.pformat(installed)))
    result = []
    for next_item in installed:
      result.append(self._installed_package(next_item['name'].lower(),
                                            next_item['version']))
    return sorted(result, key = lambda item: item.name)

  def pip(self, args):
    'Run a pip command'
    check.check_string_seq(args)

    pip_args = args + self._common_pip_args
    return self.call_pip(args)

  def call_pip(self, args, raise_error = True, stderr_to_stdout = True):
    'Call pip'

    self.check_pip_is_installed()

    self._log.log_method_d()
    self._log.log_d('call_pip: root_dir={} python_exe={}'.format(self._root_dir,
                                                                 self.python_exe))
    
    cmd = self._make_cmd_python_part() + [
      self.pip_exe,
    ] + self._common_pip_args + args
    for key, value in sorted(self.env.items()):
      self._log.log_d('call_pip: ENV: {}={}'.format(key, value))
    self._log.log_d('call_pip: cmd="{}" raise_error={}'.format(' '.join(cmd), raise_error))
    rv = execute.execute(cmd,
                         env = self.env,
                         raise_error = raise_error,
                         stderr_to_stdout = stderr_to_stdout)
    self._log.log_d('call_pip: exit_code={} stdout="{}" stderr="{}"'.format(rv.exit_code,
                                                                            rv.stdout,
                                                                            rv.stderr))
    self._cleanup_tmpdir()
    return rv

  def _make_cmd_python_part(self):
    if pip_exe.is_binary(self.pip_exe):
      cmd_python = []
    else:
      cmd_python = [ self.python_exe ]
    return cmd_python
    
  def install(self, package_name, version = None):
    'Install a package with optional version'
    check.check_string(package_name)
    check.check_string(version, allow_none = True)

    args = []
    if version:
      args.append('{}=={}'.format(package_name, version))
    else:
      args.append(package_name)
    error_message = 'Failed to install "{}" version "{}"'.format(package_name, version or '')
    self._call_install(args, error_message = error_message)

  def _call_install(self, args, error_message = None):
    args = [
      'install',
    ] + args
    rv = self.call_pip(args, raise_error = False)
    if rv.exit_code != 0:
      error_message = error_message or 'Failed to install: "{}"'.format(' '.join(args))
      error_message = error_message + ' - {}'.format(rv.stdout)
      self._log.log_w('install: {}'.format(error_message))
      raise pip_error(error_message)
    
  def install_requirements(self, requirements_files):
    'Install packages from a requirements file'
    requirements_files = object_util.listify(requirements_files)
    check.check_string_seq(requirements_files)

    for requirements_file in requirements_files:
      if not path.exists(requirements_file):
        raise pip_error(f'Requirements file not found: "{requirements_file}"')
    
    for requirements_file in requirements_files:
      self._install_one_requirements_file(requirements_file)

  def _install_one_requirements_file(self, requirements_file):
    'Install packages from a requirements file'
    new_checksum = file_util.checksum('sha256', requirements_file)
    checksum_file = self._requirements_checksum_file(requirements_file)
    
    if path.exists(checksum_file):
      old_checksum = file_util.read(checksum_file, codec = 'utf-8').strip()
      if old_checksum == new_checksum:
        self._log.log_d(f'{requirements_file}: Old and new checksum are the same')
        return
      else:
        self._log.log_d(f'{requirements_file}: Checksum changed')
    args = [
      'install',
      '-r',
      requirements_file,
    ]
    rv = self.call_pip(args, raise_error = False)
    if rv.exit_code != 0:
      msg = 'Failed to install requirements: "{}"\n{}\n'.format(requirements_file, rv.stdout)
      self._log.log_w('install: {}'.format(msg))
      raise pip_error(msg)
    self._log.log_d(f'{requirements_file}: Saving new checksum {new_checksum} to {checksum_file}')
    file_util.save(checksum_file, content = new_checksum)
    
  def _requirements_checksum_file(self, requirements_file):
    assert path.isabs(requirements_file)
    basename = path.basename(requirements_file)
    return path.join(self.root_dir, '.requirements_checksums', basename)
    
  def call_program(self, args, **kargs):
    'Call a program with the right environment'
    command_line.check_args_type(args)

    kargs = copy.deepcopy(kargs)
    
    self._log.log_method_d()
    self._log.log_d('call_program: args={}'.format(args))

    parsed_args = command_line.parse_args(args)
    self._log.log_d('call_program: parsed_args={}'.format(parsed_args))

    env = os_env.clone_current_env()
    env.update(self.env)
    PATH = env_var(env, 'PATH')
    PYTHONPATH = env_var(env, 'PYTHONPATH')
    
    if 'env' in kargs:
      kargs_env = kargs['env']
      del kargs['env']
      if 'PATH' in kargs_env:
        PATH.append(kargs_env['PATH'])
        del kargs_env['PATH']
      if 'PYTHONPATH' in kargs_env:
        PYTHONPATH.append(kargs_env['PYTHONPATH'])
        del kargs_env['PYTHONPATH']
      env.update(kargs_env)

    PATH.prepend(self.PATH)
    PYTHONPATH.prepend(self.PYTHONPATH)
    kargs['env'] = env
    self._log.log_d('call_program: env={}'.format(env))

#    kargs['shell'] = True
    kargs['check_python_script'] = False

    for key, value in sorted(env.items()):
      self._log.log_d('call_program({}): ENV: {}={}'.format(args[0], key, value))
    
    return execute.execute(parsed_args, **kargs)
    
  def _cleanup_tmpdir(self):
    if not path.isdir(self._fake_tmp_dir):
      return
    files = file_find.find(self._fake_tmp_dir, file_type = file_find.FILE_OR_LINK)
    for f in files:
      print('cleanup: {}'.format(f))

  def needs_upgrade(self, package_name):
    'Return True if package_name needs update'
    for item in self.outdated():
      if item.name == package_name:
        return True
    return False

  def version(self, package_name):
    'Return the version of an installed package'
    installed = self.installed()
    for p in self.installed():
      if p.name == package_name:
        return p.version
    raise pip_error('Package not found: "{}"'.format(package_name))
  
  def upgrade(self, packages):
    'Upgrade a package to the latest version'
    packages = object_util.listify(packages)
    check.check_string_seq(packages)

    args = [ '--upgrade' ] + list(packages)
    error_message = 'Failed to upgrade "{}"'.format(' '.join(packages))
    self._call_install(args, error_message = error_message)
  
  def program_path(self, program):
    'Return the abs path for program in the venv'
    check.check_string(program)

    if host.is_windows():
      if not filename_util.has_extension(program, 'exe', ignore_case = True):
        program = filename_util.add_extension(program, 'exe')
    return path.join(self.bin_dir, program)

  def has_program(self, program):
    'Return True if the project has program'
    check.check_string(program)

    return path.exists(self.program_path(program))
  
  @property
  def extra_env(self):
    return self._extra_env

  # These env vars cannot be overwritten by extra_env because they mess up
  # the virtual environment operations
  _EXTRA_ENV_RESTRICTIONS = {
    'PYTHONUSERBASE',
    'PYTHONPATH',
    'PATH',
    'HOME',
    'TMPDIR',
    'TMP',
    'TEMP',
  }  
  @extra_env.setter
  def extra_env(self, extra_env):
    'Set extra environment to add to the env for the project.'
    check.check_dict(extra_env, check.STRING_TYPES, check.STRING_TYPES)

    for key in extra_env.keys():
      if key in self._EXTRA_ENV_RESTRICTIONS:
        raise pip_error('Canot overwrite env var with extra_env: {}'.format(key))
        
    self._extra_env = extra_env
