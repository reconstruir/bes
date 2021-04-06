#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import copy
import json
import os
from os import path

from bes.common.check import check
from bes.property.cached_property import cached_property
from bes.python.python_installation_v2 import python_installation_v2
from bes.system.command_line import command_line
from bes.system.env_var import env_var
from bes.system.execute import execute
from bes.system.host import host
from bes.system.log import logger
from bes.system.os_env import os_env
from bes.url.url_util import url_util

from .pip_error import pip_error
from .pip_exe import pip_exe

class pip_project_v2(object):
  'Pip project.'

  _log = logger('pip')
  
  def __init__(self, name, root_dir, python_exe, debug = False):
    check.check_string(name)
    check.check_string(root_dir)

    self._python_exe = python_exe
    self._name = name
    self._root_dir = path.abspath(root_dir)
    self._droppings_dir = path.join(self.project_dir, 'droppings')
    self._pip_cache_dir = path.join(self._droppings_dir, 'pip-cache')
    self._pipenv_cache_dir = path.join(self._droppings_dir, 'pipenv-cache')
    self._fake_home_dir = path.join(self._droppings_dir, 'fake-home')
    self._user_base_dir = path.join(self.project_dir, 'py-user-base')

    self._installation = python_installation_v2(self._python_exe)

    self._common_pip_args = [
      '--cache-dir', self._pip_cache_dir,
    ]
    self._log.log_d('pip_project: pip_exe={} pip_env={} project_dir={}'.format(self.pip_exe,
                                                                               self.env,
                                                                               self.project_dir))
  @property
  def project_dir(self):
    return path.join(self._root_dir, self._name)

  @property
  def prefix_dir(self):
    return path.join(self.project_dir, 'prefix')
  
  @property
  def bin_dir(self):
    if host.is_windows():
      bin_dir = path.join(self.prefix_dir, 'Scripts')
    elif host.is_unix():
      bin_dir = path.join(self.prefix_dir, 'bin')
    else:
      host.raise_unsupported_system()
    return bin_dir
  
  @cached_property
  def env(self):
    'Make a clean environment for python or pip'
    clean_env = os_env.make_clean_env()

    env_var(clean_env, 'PYTHONUSERBASE').value = self._user_base_dir
    env_var(clean_env, 'PYTHONPATH').path = self.PYTHONPATH
    env_var(clean_env, 'PATH').prepend(self.PATH)
    env_var(clean_env, 'HOME').value = self._fake_home_dir
    return clean_env

  @cached_property
  def PYTHONPATH(self):
    return [
    ] + self._installation.PYTHONPATH

  @cached_property
  def PATH(self):
    return [
      path.dirname(self._python_exe),
      self.bin_dir,
    ] + self._installation.PATH
  
  @cached_property
  def python_exe(self):
    return self._installation.python_exe

  @cached_property
  def pip_exe(self):
    return self._installation.pip_exe
  
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
      self.pip_exe,
    ] + self._common_pip_args + args
    self._log.log_d('call_pip: cmd={}'.format(cmd))
    for key, value in sorted(self.env.items()):
      self._log.log_d('call_pip: {}={}'.format(key, value))
    rv = execute.execute(cmd, env = self.env)
    self._log.log_d('call_pip: exit_code={} stdout={} stderr={}'.format(rv.exit_code,
                                                                        rv.stdout,
                                                                        rv.stderr))
    return rv

  def _make_cmd_python_part(self):
    if pip_exe.is_binary(self.pip_exe):
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
#      '--user',
      '--prefix', self.prefix_dir,
#      '--ignore-installed',
#      '--upgrade',
#      '--python-version', self._installation.python_version,
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
    
