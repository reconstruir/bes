#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check

from bes.system.os_env import os_env
from bes.url.url_util import url_util
from bes.system.execute import execute
from bes.fs.dir_util import dir_util

from bes.python.python_exe import python_exe
from bes.python.python_version import python_version

from .pip_error import pip_error
from .pip_exe import pip_exe
from .pip_installer_options import pip_installer_options

class pip_installer(object):
  'Install pip.'

  def __init__(self, options = None):
    check.check_pip_installer_options(options, allow_none = True)
    self._options = options or pip_installer_options()
  
  _GET_PIP_URL = 'https://bootstrap.pypa.io/get-pip.py'
  
  def update(self, py_exe, pip_version):
    'Update pip to the given version or install it if needed'
    check.check_string(py_exe)
    check.check_string(pip_version)

    python_exe.check_exe(py_exe)
    version = python_exe.version(py_exe)
    exe = pip_exe.pip_exe(py_exe)
    if pip_exe.pip_exe_is_valid(exe):
      self._update_pip(py_exe, pip_version)
    else:
      self._install_pip(py_exe, pip_version)

    if not pip_exe.pip_exe_is_valid(exe):
      raise pip_error('failed to install: "{}"'.format(exe))
    
  def _install_pip(self, py_exe, pip_version):
    'Install pip from scratch'
    tmp_get_pip = url_util.download_to_temp_file(self._GET_PIP_URL)
    cmd = [ py_exe, tmp_get_pip ]
    execute.execute(cmd, env = self._make_clean_env())
    exe = pip_exe.pip_exe(py_exe)
    if not pip_exe.pip_exe_is_valid(exe):
      raise pip_error('failed to install pip version {}'.format(pip_version))
    self._update_pip(py_exe, pip_version)

  def _update_pip(self, py_exe, pip_version):
    'Update pip to the given version or install it if needed'
    check.check_string(py_exe)
    check.check_string(pip_version)

    python_exe.check_exe(py_exe)
    version = python_exe.version(py_exe)
    exe = pip_exe.pip_exe(py_exe)
    old_pip_version = pip_exe.version(exe)
    if old_pip_version == pip_version:
      return
    cmd = [ exe, 'install', 'pip=={}'.format(pip_version) ]
    execute.execute(cmd, env = self._make_clean_env())
  
  @classmethod
  def _list_python_dir(clazz, py_exe):
    python_bin_dir = path.dirname(py_exe)
    return dir_util.list(python_bin_dir)

  def status(self, py_exe):
    'Return the current pip situation'
    check.check_string(py_exe)
    
    if not path.isabs(py_exe):
      raise pip_error('py_exe needs to be an absolute path')
    
    version = python_version.version(py_exe)
    tmp_get_pip = url_util.download_to_temp_file(self, url._GET_PIP_URL)
    cmd = [ py_exe, tmp_get_pip ]
    env = os_env.clone_current_env(d = { 'PYTHONPATH': ''})
    list_before = self._list_python_dir(py_exe)
    execute.execute(cmd, env = env)
    list_after = self._list_python_dir(py_exe)
    pip_basename = 'pip{}'.format(version)
    pip_exe = next(iter([ f for f in list_after if f.endswith(pip_basename) ]), None)
    if not pip_exe:
      raise pip_error('failed to install {}'.format(pip_basename))
    cmd = [ pip_exe, 'install', 'pip=={}'.format(pip_version) ]
    execute.execute(cmd, env = env)
    return pip_exe

  @classmethod
  def _make_clean_env(clazz):
    'Make a clean environment for python or pip'
    changes = {
      'PYTHONPATH': '',
    }
    return os_env.clone_current_env(d = changes)

  def uninstall(self, py_exe):
    'Uninstall pip for the given python executable'
    check.check_string(py_exe)

    python_exe.check_exe(py_exe)
    exe = pip_exe.pip_exe(py_exe)
    if not pip_exe.pip_exe_is_valid(exe):
      return
    cmd = [ exe, 'uninstall', '--yes', 'pip' ]
    execute.execute(cmd, env = self._make_clean_env())
