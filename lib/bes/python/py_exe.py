#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.fs.file_path import file_path
from bes.system.host import host

class py_exe(object):
  'Class to deal with the python executable.'

  @classmethod
  def find_python_exe(clazz):
    'Return the full path to the platform specific python executable.'
    exe_name = clazz._python_exe_name()
    exe = file_path.which(exe_name)
    return exe

  @classmethod
  def _python_exe_name(clazz):
    'Return the platform specific name of the python exe.'
    if host.is_unix():
      return 'python'
    elif host.is_windows():
      return 'python.exe'
    else:
      host.raise_unsupported_system()
