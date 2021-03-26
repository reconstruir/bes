#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import copy
import json
from os import path

from bes.common.check import check
from bes.property.cached_property import cached_property
from bes.python.python_exe import python_exe as bes_python_exe
from bes.python.python_installation import python_installation
from bes.system.command_line import command_line
from bes.system.env_var import env_var
from bes.system.execute import execute
from bes.system.host import host
from bes.system.log import logger
from bes.system.os_env import os_env
from bes.url.url_util import url_util

from .pip_error import pip_error
from .pip_exe import pip_exe

class pip_project(object):
  'Pip project.'

  _log = logger('pip')
  
  def __init__(self, name, root_dir, python_exe, debug = False):
    check.check_string(name)
    check.check_string(root_dir)
    bes_python_exe.check_exe(python_exe)

    self._python_exe = python_exe
    self._python_version = bes_python_exe.version(self._python_exe)
    self._name = name
    self._root_dir = root_dir
    self._project_dir = path.join(self._root_dir, self._name)
    self._droppings_dir = path.join(self._project_dir, 'droppings')
    self._pip_cache_dir = path.join(self._droppings_dir, 'pip-cache')
    self._pipenv_cache_dir = path.join(self._droppings_dir, 'pipenv-cache')
    self._fake_home_dir = path.join(self._droppings_dir, 'fake-home')
    self._user_base_dir = path.join(self._project_dir, 'py-user-base')
    
    self._installation = python_installation(self._user_base_dir,
                                             self._python_version)

    self._common_pip_args = [
      '--cache-dir', self._pip_cache_dir,
    ]
    self._log.log_d('pip_project: pip_exe={} site_packages_dir={} pip_env={} project_dir={}'.format(self.exe,
                                                                                                    self.site_packages_dir,
                                                                                                    self.env,
                                                                                                    self._project_dir))
  @property
  def project_dir(self):
    return self._project_dir

  @cached_property
  def env(self):
    'Make a clean environment for python or pip'
    extra_env = {
      'PYTHONUSERBASE': self._user_base_dir,
      'PYTHONPATH': self.site_packages_dir,
      'HOME': self._fake_home_dir,
    }
    return os_env.make_clean_env(update = extra_env, allow_override = True)

  @cached_property
  def PYTHONPATH(self):
    return self._installation.PYTHONPATH

  @cached_property
  def PATH(self):
    return [
      path.dirname(self._python_exe),
    ] + self._installation.PATH
  
  @cached_property
  def exe(self):
    return self._installation.exe

  @cached_property
  def site_packages_dir(self):
    return self._installation.site_packages_dir

  @property
  def pip_version(self):
    return pip_exe.version(self.exe)
  
  def pip_is_installed(self):
    'Return True if pip is installed'
    return path.exists(self.exe)

  def check_pip_is_installed(self):
    'Check that pip is installed and if not raise an error'
    if not self.pip_is_installed():
      raise pip_error('Pip not found: {}'.format(self.exe))

  _outdated_package = namedtuple('_outdated_package', 'name, current_version, latest_version, latest_filetype')
  def outdated(self):
    'Return a dictionary of outdated packages'
    args = [
      'list',
      '--user',
      '--outdated',
      '--format', 'json',
    ]
    rv = self.call_pip(args)
    outdated = json.loads(rv.stdout)
    result = {}
    for next_item in outdated:
      op = self._outdated_package(next_item['name'],
                                  next_item['version'],
                                  next_item['latest_version'],
                                  next_item['latest_filetype'])
      result[op.name] = op
    return result

  def pip(self, args):
    'Run a pip command'
    check.check_string_seq(args)

    pip_args = args + self._common_pip_args
    return self.call_pip(args)

  def call_pip(self, args):
    'Call pip'

    self.check_pip_is_installed()

    self._log.log_method_d()
    self._log.log_d('call_pip: root_dir={} python_exe={}'.format(self._root_dir,
                                                                 self._python_exe))
    
    cmd = self._make_cmd_python_part() + [
      self.exe,
    ] + self._common_pip_args + args
    self._log.log_d('call_pip: cmd={} env={}'.format(cmd, self.env))
    rv = execute.execute(cmd, env = self.env)
    return rv

  def _make_cmd_python_part(self):
    if pip_exe.is_binary(self.exe):
      cmd_python = []
    else:
      cmd_python = [ self._python_exe ]
    return cmd_python
    
  def install(self, package_name, version = None):
    'Install a packagepackages'
    if version:
      package_args = [ '{}=={}'.format(package_name, version) ]
    else:
      package_args = [ package_name ]
    args = [
      'install',
      '--user',
    ] + package_args
    self.call_pip(args)

  def call_program(self, args, **kargs):
    'Call a program with the right environment'
    command_line.check_args_type(args)

    kargs = copy.deepcopy(kargs)
    
    self._log.log_method_d()
    self._log.log_d('call_program: args={}'.format(args))

    parsed_args = command_line.parse_args(args)
    self._log.log_d('call_program: parsed_args={}'.format(parsed_args))

    env = os_env.clone_current_env()
    env['HOME'] = self._fake_home_dir
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

    kargs['shell'] = True
    kargs['check_python_script'] = False
    
    return execute.execute(parsed_args, **kargs)
    
