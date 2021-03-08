#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, os

from .host import host

class which(object):
  'Find executables in the system just like unix which.'

  @classmethod
  def _is_executable(clazz, p):
    'Return True if the path is executable.'
    return path.exists(p) and os.access(p, os.X_OK)

  @classmethod
  def which(clazz, program, raise_error = False):
    '''
    Return the absolute path for program or None.
    raise_error will optionally raise a RuntimeError exception if not found.
    '''
    if path.isabs(program) and clazz._is_executable(program):
      return program
      
    fpath, fname = path.split(program)
    if fpath:
      if clazz._is_executable(program):
        return program
    else:
      possible_programs = clazz._possible_program_names(program)
      for next_path in os.environ['PATH'].split(os.pathsep):
        for possible_program in possible_programs:
          exe_file = path.join(next_path, possible_program)
          if clazz._is_executable(exe_file):
            return exe_file
    if raise_error:
      raise RuntimeError('Executable for %s not found.  Fix your PATH.' % (program))
    return None

  @classmethod
  def _possible_program_names(clazz, program):
    'Return possible names for a program taking into account extensions'
    # If the program already has an extension then use just that
    if program.rfind('.') >= 0:
      return ( program, )
    if host.is_windows():
      return (
        program,
        program + '.exe',
        program + '.bat',
        program + '.cmd',
        program + '.ps1',
        program + '.py',
      )
    elif host.is_unix():
      return (
        program,
        program + '.py',
      )
    else:
      host.raise_unsupported_system()
