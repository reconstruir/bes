#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path
from .host import host

class python(object):
  'Class to deal with system specific python things.'

  @classmethod
  def find_python_exe(clazz):
    'Return the full path to the platform specific python executable.'
    exe_name = clazz._python_exe_name()
    return clazz._find_program(exe_name)
    
  @classmethod
  def _python_exe_name(clazz):
    'Return the platform specific name of the python exe.'
    if host.is_unix():
      return 'python'
    elif host.is_windows():
      return 'python.exe'
    else:
      host.raise_unsupported_system()

  @classmethod
  def _find_program(clazz, program):
    'Find a program in PATH.'
    for p in os.environ['PATH'].split(os.pathsep):
      program_filename = path.join(p, program)
      if path.exists(program_filename):
        return program_filename
    return None
  
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
