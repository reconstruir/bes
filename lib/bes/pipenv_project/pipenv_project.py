#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#from collections import namedtuple
#import copy
#import json
#import os
#from os import path
#import pprint
#
from bes.common.check import check
#from bes.fs.file_util import file_util
#from bes.fs.file_find import file_find
#from bes.property.cached_property import cached_property
#from bes.system.command_line import command_line
#from bes.system.env_var import env_var
#from bes.system.execute import execute
#from bes.system.host import host
from bes.system.log import logger
#from bes.system.os_env import os_env
#from bes.url.url_util import url_util
#
#from .pipenv_project_error import pipenv_project_error
#from .pip_exe import pip_exe
#from .python_installation import python_installation
#from .python_source import python_source
#from .python_version import python_version
#from .python_virtual_env import python_virtual_env

from bes.python.pip_project import pip_project
from bes.python.pip_project_options import pip_project_options

from .pipenv_project_options import pipenv_project_options

class pipenv_project(object):
  'Pipenv project.'

  _log = logger('pipenv')
  
  def __init__(self, options = None):
    check.check_pipenv_project_options(options, allow_none = True)

    self._options = options or pipenv_project_options()
    pp_options = pip_project_options(debug = self._options.debug,
                                     verbose = self._options.verbose,
                                     blurber = self._options.blurber,
                                     root_dir = self._options.root_dir,
                                     python_version = self._options.python_version,
                                     name = self._options.name)
    self._pip_project = pip_project(pp_options.name,
                                    pp_options.root_dir,
                                    pp_options.resolve_python_exe(),
                                    debug = pp_options.debug)
      
  @property
  def pip_project(self):
    return self._pip_project

######  @cached_property
######  def installation(self):
######    return self.virtual_env.installation
######
######  @cached_property
######  def python_exe(self):
######    return self.installation.python_exe
######  
######  @cached_property
######  def project_dir(self):
######    return path.join(self._root_dir, self._name)
######
######  @cached_property
######  def user_base_install_dir(self):
######    if host.is_windows():
######      user_base_install_dir = path.join(self.project_dir, self.installation.windows_versioned_install_dirname)
######    elif host.is_unix():
######      user_base_install_dir = self.project_dir
######    else:
######      host.raise_unsupported_system()
######    return user_base_install_dir
######  
######  @cached_property
######  def bin_dir(self):
######    if host.is_windows():
######      bin_dir = path.join(self.user_base_install_dir, 'Scripts')
######    elif host.is_unix():
######      bin_dir = path.join(self.user_base_install_dir, 'bin')
######    else:
######      host.raise_unsupported_system()
######    return bin_dir
######  
######  @cached_property
######  def site_packages_dir(self):
######    if host.is_windows():
######      site_packages_dir = path.join(self.user_base_install_dir, 'site-packages')
######    elif host.is_unix():
######      site_packages_dir = path.join(self.user_base_install_dir, 'lib/python/site-packages')
######    else:
######      host.raise_unsupported_system()
######    return site_packages_dir
######  
######  @cached_property
######  def env(self):
######    'Make a clean environment for python or pip'
######    clean_env = os_env.make_clean_env()
######
######    env_var(clean_env, 'PYTHONUSERBASE').value = self.project_dir
######    env_var(clean_env, 'PYTHONPATH').path = self.PYTHONPATH
######    env_var(clean_env, 'PATH').prepend(self.PATH)
######    env_var(clean_env, 'HOME').value = self._fake_home_dir
######    env_var(clean_env, 'TMPDIR').value = self._fake_tmp_dir
######    env_var(clean_env, 'TMP').value = self._fake_tmp_dir
######    env_var(clean_env, 'TEMP').value = self._fake_tmp_dir
######    return clean_env
######
######  @cached_property
######  def PYTHONPATH(self):
######    return self.installation.PYTHONPATH + [
######      self.site_packages_dir,
######    ]
######
######  @cached_property
######  def PATH(self):
######    return [
######      path.dirname(self.python_exe),
######      self.bin_dir,
######    ] + self.installation.PATH
######  
######  @cached_property
######  def python_exe(self):
######    return self.installation.python_exe
######
######  @cached_property
######  def pip_exe(self):
######    return self.installation.pip_exe
######
######  def activate_script(self, variant = None):
######    'Return the activate script for the virtual env'
######    return python_source.virtual_env_activate_script(self.project_dir, variant)
######  
######  @property
######  def pip_version(self):
######    return pip_exe.version(self.pip_exe)
######  
######  def pip_is_installed(self):
######    'Return True if pip is installed'
######    return self.pip_exe and path.exists(self.pip_exe)
######
######  def check_pip_is_installed(self):
######    'Check that pip is installed and if not raise an error'
######    if not self.pip_is_installed():
######      raise pipenv_project_error('Pip not found: {}'.format(self.pip_exe or ''))
######
######  _outdated_package = namedtuple('_outdated_package', 'name, current_version, latest_version, latest_filetype')
######  def outdated(self):
######    'Return a dictionary of outdated packages'
######    args = [
######      'list',
######      '--outdated',
######      '--format', 'json',
######    ]
######    rv = self.call_pip(args, stderr_to_stdout = False)
######    outdated = json.loads(rv.stdout)
######
######    result = {}
######    for next_item in outdated:
######      op = self._outdated_package(next_item['name'].lower(),
######                                  next_item['version'],
######                                  next_item['latest_version'],
######                                  next_item['latest_filetype'])
######      result[op.name] = op
######    self._log.log_d('outdated: outdated={}'.format(pprint.pformat(result)))
######    return result
######
######  _installed_package = namedtuple('_installed_package', 'name, version')
######  def installed(self):
######    'Return a list of installed packages'
######    args = [
######      'list',
######      '--format', 'json',
######    ]
######    rv = self.call_pip(args, stderr_to_stdout = False)
######    installed = json.loads(rv.stdout)
######    self._log.log_d('installed: installed={}'.format(pprint.pformat(installed)))
######    result = []
######    for next_item in installed:
######      result.append(self._installed_package(next_item['name'].lower(),
######                                            next_item['version']))
######    return sorted(result, key = lambda item: item.name)
######  
######  def pip(self, args):
######    'Run a pip command'
######    check.check_string_seq(args)
######
######    pip_args = args + self._common_pip_args
######    return self.call_pip(args)
######
######  def call_pip(self, args, raise_error = True, stderr_to_stdout = True):
######    'Call pip'
######
######    self.check_pip_is_installed()
######
######    self._log.log_method_d()
######    self._log.log_d('call_pip: root_dir={} python_exe={}'.format(self._root_dir,
######                                                                 self.python_exe))
######    
######    cmd = self._make_cmd_python_part() + [
######      self.pip_exe,
######    ] + self._common_pip_args + args
######    for key, value in sorted(self.env.items()):
######      self._log.log_d('call_pip: ENV: {}={}'.format(key, value))
######    self._log.log_d('call_pip: cmd="{}" raise_error={}'.format(' '.join(cmd), raise_error))
######    rv = execute.execute(cmd,
######                         env = self.env,
######                         raise_error = raise_error,
######                         stderr_to_stdout = stderr_to_stdout)
######    self._log.log_d('call_pip: exit_code={} stdout="{}" stderr="{}"'.format(rv.exit_code,
######                                                                            rv.stdout,
######                                                                            rv.stderr))
######    self._cleanup_tmpdir()
######    return rv
######
######  def _make_cmd_python_part(self):
######    if pip_exe.is_binary(self.pip_exe):
######      cmd_python = []
######    else:
######      cmd_python = [ self.python_exe ]
######    return cmd_python
######    
######  def install(self, package_name, version = None):
######    'Install a package with optional version'
######    check.check_string(package_name)
######    check.check_string(version, allow_none = True)
######
######    args = []
######    if version:
######      args.append('{}=={}'.format(package_name, version))
######    else:
######      args.append(package_name)
######    error_message = 'Failed to install "{}" version "{}"'.format(package_name, version or '')
######    self._call_install(args, error_message = error_message)
######
######  def _call_install(self, args, error_message = None):
######    args = [
######      'install',
######    ] + args
######    rv = self.call_pip(args, raise_error = False)
######    if rv.exit_code != 0:
######      error_message = error_message or 'Failed to install: "{}"'.format(' '.join(args))
######      error_message = error_message + ' - {}'.format(rv.stdout)
######      self._log.log_w('install: {}'.format(error_message))
######      raise pipenv_project_error(error_message)
######    
######  def install_requirements(self, requirements_file):
######    'Install packages from a requirements file'
######    check.check_string(requirements_file)
######    
######    args = [
######      'install',
######      '-r',
######      requirements_file,
######    ]
######    rv = self.call_pip(args, raise_error = False)
######    if rv.exit_code != 0:
######      msg = 'Failed to install requirements: "{}"\n{}\n'.format(requirements_file, rv.stdout)
######      self._log.log_w('install: {}'.format(msg))
######      raise pipenv_project_error(msg)
######    
######  def call_program(self, args, **kargs):
######    'Call a program with the right environment'
######    command_line.check_args_type(args)
######
######    kargs = copy.deepcopy(kargs)
######    
######    self._log.log_method_d()
######    self._log.log_d('call_program: args={}'.format(args))
######
######    parsed_args = command_line.parse_args(args)
######    self._log.log_d('call_program: parsed_args={}'.format(parsed_args))
######
######    env = os_env.clone_current_env()
######    env['HOME'] = self._fake_home_dir
######    PATH = env_var(env, 'PATH')
######    PYTHONPATH = env_var(env, 'PYTHONPATH')
######    
######    if 'env' in kargs:
######      kargs_env = kargs['env']
######      del kargs['env']
######      if 'PATH' in kargs_env:
######        PATH.append(kargs_env['PATH'])
######        del kargs_env['PATH']
######      if 'PYTHONPATH' in kargs_env:
######        PYTHONPATH.append(kargs_env['PYTHONPATH'])
######        del kargs_env['PYTHONPATH']
######      env.update(kargs_env)
######
######    PATH.prepend(self.PATH)
######    PYTHONPATH.prepend(self.PYTHONPATH)
######    kargs['env'] = env
######    self._log.log_d('call_program: env={}'.format(env))
######
######    kargs['shell'] = True
######    kargs['check_python_script'] = False
######    
######    return execute.execute(parsed_args, **kargs)
######    
######  def _cleanup_tmpdir(self):
######    if not path.isdir(self._fake_tmp_dir):
######      return
######    files = file_find.find(self._fake_tmp_dir, file_type = file_find.FILE_OR_LINK)
######    for f in files:
######      print('cleanup: {}'.format(f))
######
######  def needs_upgrade(self, package_name):
######    'Return True if package_name needs update'
######    return package_name in self.outdated()
######
######  def version(self, package_name):
######    'Return the version of an installed package'
######    installed = self.installed()
######    for p in self.installed():
######      print('checking {} vs {}'.format(p.name, package_name))
######      if p.name == package_name:
######        print('found {} {}'.format(package_name, p.version))
######        return p.version
######    raise pipenv_project_error('Package not found: "{}"'.format(package_name))
######  
######  def upgrade(self, package_name):
######    'Upgrade a package to the latest version'
######    check.check_string(package_name)
######
######    args = [ '--upgrade', package_name ]
######    error_message = 'Failed to upgrade "{}"'.format(package_name)
######    self._call_install(args, error_message = error_message)
######  
######  def program_path(self, program):
######    'Return the abs path for program in the venv'
######    check.check_string(program)
######
######    return path.join(self.bin_dir, program)
