#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import glob
from os import path

from bes.property.cached_property import cached_property
from bes.system.check import check
from bes.system.execute import execute
from bes.system.host import host
from bes.system.log import logger

from . import uv_error

class uv_venv(object):
  'Low-level uv virtual environment management.'

  _log = logger('uv_venv')

  def __init__(self, root_dir, uv_exe_path, python=None):
    check.check_string(root_dir)
    check.check_string(uv_exe_path)
    check.check_string(python, allow_none=True)

    self._root_dir = path.abspath(root_dir)
    self._uv_exe_path = uv_exe_path
    self._python = python

  @property
  def root_dir(self):
    return self._root_dir

  def create(self):
    'Create the virtual environment if it does not already exist.'
    if self.is_valid():
      self._log.log_d(f'create: venv already valid at {self._root_dir}')
      return
    command = [self._uv_exe_path, 'venv']
    if self._python:
      command += ['--python', self._python]
    command.append(self._root_dir)
    self._log.log_d(f'create: running {command}')
    execute.execute(command, raise_error=True, stderr_to_stdout=True, check_python_script=False)

  def is_valid(self):
    'Return True if the venv has a pyvenv.cfg and an executable python.'
    cfg = path.join(self._root_dir, 'pyvenv.cfg')
    if not path.isfile(cfg):
      return False
    python_exe = self._find_python_exe()
    return python_exe is not None and path.isfile(python_exe)

  @cached_property
  def python_exe(self):
    result = self._find_python_exe()
    if not result:
      raise uv_error.uv_error(f'Python executable not found in venv at {self._root_dir}')
    return result

  @cached_property
  def bin_dir(self):
    if host.is_windows():
      return path.join(self._root_dir, 'Scripts')
    return path.join(self._root_dir, 'bin')

  @cached_property
  def site_packages_dir(self):
    if host.is_windows():
      return path.join(self._root_dir, 'Lib', 'site-packages')
    pattern = path.join(self._root_dir, 'lib', 'python*', 'site-packages')
    matches = sorted(glob.glob(pattern))
    if matches:
      return matches[-1]
    raise uv_error.uv_error(f'site-packages directory not found in {self._root_dir}')

  def activate_script(self, variant=None):
    'Return the path to the venv activate script.'
    if host.is_windows():
      if variant == 'fish':
        return path.join(self.bin_dir, 'activate.fish')
      elif variant == 'csh':
        return path.join(self.bin_dir, 'activate.csh')
      return path.join(self.bin_dir, 'activate.bat')
    if variant == 'fish':
      return path.join(self.bin_dir, 'activate.fish')
    elif variant == 'csh':
      return path.join(self.bin_dir, 'activate.csh')
    return path.join(self.bin_dir, 'activate')

  def _find_python_exe(self):
    if host.is_windows():
      candidate = path.join(self._root_dir, 'Scripts', 'python.exe')
    else:
      candidate = path.join(self._root_dir, 'bin', 'python')
    return candidate if path.isfile(candidate) else None
