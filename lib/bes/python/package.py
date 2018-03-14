#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, pkgutil
from bes.fs import file_path, temp_file

class package(object):
  'Class to deal with python packages.'

  @classmethod
  def get_data_program_exe(clazz, program_path, filename, module_name):
    if path.isabs(program_path):
      raise ValueError('program_path should be relative instead of absolute: %s' % (program_path))
    program_path_abs = path.normpath(path.join(path.dirname(filename), program_path))
    if path.exists(program_path_abs):
      if not file_path.is_executable(program_path_abs):
        raise RuntimeError('not an executable program: %s' % (program_path_abs))
      return program_path_abs
    exe_data = pkgutil.get_data(module_name, program_path)
    if not exe_data:
      raise RuntimeError('data for program_path \"%s\" not found in module_name \"%s\"' % (program_path, module_name))
    exe_tmp = temp_file.make_temp_file(content = exe_data, prefix = path.basename(program_path_abs) + '-')
    os.chmod(exe_tmp, 0o755)
    return exe_tmp
