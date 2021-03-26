#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import json
from os import path

from bes.common.check import check

from bes.fs.dir_util import dir_util
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.system.execute import execute
from bes.system.host import host
from bes.system.log import logger
from bes.system.os_env import os_env
from bes.url.url_util import url_util

from bes.python.python_exe import python_exe as bes_python_exe

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
    self._name = name
    self._root_dir = root_dir
    self._cache_dir = path.join(self._root_dir, '.pip_cache')
    self._install_dir = path.join(self._root_dir, self._name)
    self._common_pip_args = [
      '--cache-dir', self._cache_dir,
    ]
    self._pip_exe = self._determine_pip_exe()
    self._pip_site_packages_dir = self._determine_pip_site_packages_dir()
    self._pip_env = self._make_env()
    self._log.log_d('pip_project: pip_exe={} site_packages_dir={} pip_env={} install_dir={}'.format(self._pip_exe,
                                                                                                    self._pip_site_packages_dir,
                                                                                                    self._pip_env,
                                                                                                    self._install_dir))

  @property
  def env(self):
    return self._pip_env

  @property
  def exe(self):
    return self._pip_exe

  @property
  def site_packages_dir(self):
    return self._pip_site_packages_dir

  @property
  def pip_version(self):
    return pip_exe.version(self.exe)
  
  def pip_is_installed(self):
    'Return True if pip is installed'
    return path.exists(self._pip_exe)

  def check_pip_is_installed(self):
    'Check that pip is installed and if not raise an error'
    if not self.pip_is_installed():
      raise pip_error('Pip not found: {}'.format(self._pip_exe))

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
      self._pip_exe,
    ] + self._common_pip_args + args
    self._log.log_d('call_pip: cmd={} env={}'.format(cmd, self._pip_env))
    rv = execute.execute(cmd, env = self._pip_env)
    return rv

  def _determine_pip_exe(self):
    'Determine the pip executable for this installation'
    python_exe_version = bes_python_exe.version(self._python_exe)
    if host.is_windows():
      pip_exe_basename = 'pip{}.exe'.format(python_exe_version)
      python_dir = 'Python{}'.format(python_exe_version.replace('.', ''))
      if python_exe_version == '2.7':
        pexe = path.join(self._install_dir, 'Scripts', pip_exe_basename)
      else:
        pexe = path.join(self._install_dir, python_dir, 'Scripts', pip_exe_basename)
    elif host.is_unix():
      pip_exe_basename = 'pip{}'.format(python_exe_version)
      pexe = path.join(self._install_dir, 'bin', pip_exe_basename)
    else:
      host.raise_unsupported_system()
    return pexe

  def _determine_pip_site_packages_dir(self):
    'Determine the pip site-packages dir sometimes needed for PYTHONPATH'
    python_exe_version = bes_python_exe.version(self._python_exe)
    if host.is_windows():
      python_dir = 'Python{}'.format(python_exe_version.replace('.', ''))
      #if python_exe_version == '2.7':
      #  site_packaged_dir = path.join(self._install_dir, 'site-packages')
      #else:
      site_packaged_dir = path.join(self._install_dir, python_dir, 'site-packages')
    elif host.is_unix():
      site_packaged_dir = path.join(self._install_dir, 'lib/python/site-packages')
    else:
      host.raise_unsupported_system()
    return site_packaged_dir
  
  def _make_cmd_python_part(self):
    if pip_exe.is_binary(self._pip_exe):
      cmd_python = []
    else:
      cmd_python = [self._python_exe]
    return cmd_python
    
  def _make_env(self):
    'Make a clean environment for python or pip'
    extra_env = {
      'PYTHONUSERBASE': self._install_dir,
      'PYTHONPATH': self.site_packages_dir,
    }
    return os_env.make_clean_env(update = extra_env)
    
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
