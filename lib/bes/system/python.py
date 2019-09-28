#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from .host import host
from .which import which

class python(object):
  'Class to deal with system specific python things.'

  @classmethod
  def find_python_exe(clazz):
    'Return the full path to the platform specific python executable.'
    exe_name = clazz._python_exe_name()
    return which.which(exe_name)

  _UNIX_POSSIBLE_EXE = [ 'python3', 'python2', 'python' ]
  @classmethod
  def _python_exe_name(clazz):
    'Return the platform specific name of the python exe.'
    if host.is_unix():
      for exe in clazz._UNIX_POSSIBLE_EXE:
        if which.which(exe):
          return path.basename(exe)
      raise RuntimeError('python not found.')
    elif host.is_windows():
      return 'python.exe'
    else:
      host.raise_unsupported_system()

  @classmethod
  def is_python_script(clazz, filename):
    if filename.lower().endswith('.py'):
      return True
    try:
      with open(filename, 'r') as fin:
        content = fin.read(32)
        return content.startswith('#!/usr/bin/env python')
        return result
    except Exception as ex:
      pass
    return False
