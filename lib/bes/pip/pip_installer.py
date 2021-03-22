#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check

from bes.fs.dir_util import dir_util
from bes.fs.file_util import file_util
from bes.system.execute import execute
from bes.system.log import logger
from bes.system.os_env import os_env
from bes.url.url_util import url_util

from bes.python.python_exe import python_exe
from bes.python.python_version import python_version

from .pip_error import pip_error
from .pip_exe import pip_exe
from .pip_installer_options import pip_installer_options
from .pip_project import pip_project

class pip_installer(object):
  'Pip installer.'

  _log = logger('pip')
  
  def __init__(self, options = None):
    check.check_pip_installer_options(options, allow_none = True)

    self._options = options or pip_installer_options()
    self._python_exe = self._options.resolve_python_exe()
    python_exe.check_exe(self._python_exe)
    self._root_dir = self._options.resolve_root_dir()
    self._cache_dir = path.join(self._root_dir, '.pip_cache')
    self._install_dir = path.join(self._root_dir, self._options.name)
    self._common_pip_args = [
      '--cache-dir', self._cache_dir,
    ]
    self._project = pip_project(self._options)
    
  _GET_PIP_27_URL = 'https://bootstrap.pypa.io/pip/2.7/get-pip.py'
  _GET_PIP_36_URL = 'https://bootstrap.pypa.io/get-pip.py'

  def install(self, pip_version, clobber_install_dir):
    'Install pip on an empty root directory'
    check.check_string(pip_version)
    check.check_bool(clobber_install_dir)

    self._log.log_method_d()
    self._log.log_d('install: root_dir={} python_exe={}'.format(self._root_dir,
                                                                self._python_exe))

    if path.exists(self._install_dir):
      if not path.isdir(self._install_dir):
        raise pip_error('Not a directory: "{}"'.format(self._install_dir))
      if clobber_install_dir:
        file_util.remove(self._install_dir)
      if path.isdir(self._install_dir) and not dir_util.is_empty(self._install_dir):
        raise pip_error('Directory not empty: "{}"'.format(self._install_dir))

    url = self._determine_get_pip_url(self._python_exe)
    tmp_get_pip = url_util.download_to_temp_file(url, suffix = '.py')
    self._log.log_d('install: url={} tmp_get_pip={}'.format(url, tmp_get_pip))
      
    cmd = [
      self._python_exe,
      tmp_get_pip,
      'install',
      '--user',
    ] + self._common_pip_args
    file_util.mkdir(self._root_dir)
    self._log.log_d('install: cmd={} env={}'.format(cmd, self._project.env))
    execute.execute(cmd, env = self._project.env)
    if pip_version == 'latest':
      outdated = self._project.outdated()
      op = outdated.get('pip', None)
      if op:
        self._log.log_d('install: need to update pip to'.format(op.latest_version))
        self._update_pip(op.latest_version)
    else:
      self._update_pip(pip_version)
    
  def update(self, pip_version):
    'Update pip to the given version or install it if needed'
    check.check_string(pip_version)

    if not self._project.pip_is_installed():
      self.install(pip_version, False)
      
    self._update_pip(pip_version)

  def is_installed(self):
    'Return True if pip is installed'
    return self._project.pip_is_installed()

  def pip_version(self):
    'Return the pip version'
    return self._project.pip_version
  
  def pip_exe(self):
    'Return the pip exe'
    return self._project.exe
  
  def _update_pip(self, pip_version):
    'Update pip to the given version or install it if needed'

    self._project.check_pip_is_installed()

    old_pip_version = self._project.pip_version
    if old_pip_version == pip_version:
      return
    
    args = [
      'install',
      '--user',
      'pip=={}'.format(pip_version),
    ]
    self._project.call_pip(args)

  def uninstall(self):
    'Uninstall pip for the given python executable'

    self._project.check_pip_is_installed()

    args = [
      'uninstall',
      '--yes',
      'pip',
    ]
    self._project.call_pip(args)
    
  def _determine_get_pip_url(clazz, py_exe):
    version = python_exe.version(py_exe)
    if version == '2.7':
      return clazz._GET_PIP_27_URL
    major, minor = version.split('.')
    major = int(major)
    minor = int(minor)
    if major == 3:
      if minor >= 6:
        return clazz._GET_PIP_36_URL
    raise pip_error('Unsupported python version "{}" for {}'.format(version, py_exe))
