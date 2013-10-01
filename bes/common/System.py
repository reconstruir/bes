#!/usr/bin/env python
#-*- coding:utf-8 -*-

from Path import Path
from Shell import Shell

import os, os.path as path, platform

class System(object):
  'System'

  @staticmethod
  def which(program, raise_error = False):
    'Same as unix which.'

    fpath, fname = path.split(program)
    if fpath:
      if Path.is_executable(program):
        return program
    else:
      for p in os.environ['PATH'].split(os.pathsep):
        exe_file = path.join(p, program)
        if Path.is_executable(exe_file):
          return exe_file
    if raise_error:
      raise RuntimeError('Executable for %s not found.  Fix your PATH.' % (program))
    return None

  @staticmethod
  def is_mac():
    return platform.system() == 'Darwin'

  @staticmethod
  def is_linux():
    return platform.system() == 'Linux'

  @staticmethod
  def tty():
    return Shell.execute('tty').stdout.strip()

