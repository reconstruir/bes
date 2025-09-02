#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, os

from .host import host

class which(object):
  'Find executables in the system just like unix which.'

  if host.is_windows():
    EXE_EXTENSIONS = ( 'bat', 'cmd', 'exe', 'ps1', 'py' )
  elif host.is_unix():
    EXE_EXTENSIONS = ( 'py', )
  else:
    host.raise_unsupported_system()
    
  @classmethod
  def _is_executable(clazz, p):
    'Return True if the path is executable.'
    return path.exists(p) and os.access(p, os.X_OK)

  @classmethod
  def which(clazz, program, raise_error = False, extra_path = None):
    '''
    Return the absolute path for program or None.
    raise_error will optionally raise a RuntimeError exception if not found.
    '''
    extra_path = extra_path or []
    if path.isabs(program) and clazz._is_executable(program):
      return program
      
    fpath, fname = path.split(program)
    if fpath:
      if clazz._is_executable(program):
        return program
    else:
      env_path = os.environ['PATH'].split(os.pathsep) + extra_path
      possible_programs = clazz._possible_program_names(program)
      for next_path in env_path:
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
    ext = clazz._extension(program)
    if ext in set(clazz.EXE_EXTENSIONS):
      return ( program, )
    return tuple([ program ] + [ program + os.extsep + ext for ext in clazz.EXE_EXTENSIONS ])

  @classmethod
  def _extension(clazz, filename):
    'Return the extension for filename.'
    _, ext = path.splitext(filename)
    if ext == '':
      return None
    assert ext[0] == os.extsep
    return ext[1:]

  def test_which(self):
    'Test which()  Looks like a windows only test but works on unix as well.'
    tmp_dir = self.make_temp_dir()
    bin_dir = path.join(tmp_dir, 'bin')
    content = '@echo off\n\recho kiwi\n\rexit 0\n\r'
    temp_bat = file_util.save(path.join(bin_dir, 'kiwi_tool.bat'), content = content, mode = 0o0755)
    self.assertEqual( None, which.which('kiwi_tool.bat') )
    with env_override.path_append([ bin_dir ]) as env:
      expected_path = path.join(bin_dir, 'kiwi_tool.bat')
      self.assertEqual( expected_path, which.which('kiwi_tool.bat') )
  
