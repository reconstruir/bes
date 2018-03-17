#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, pkgutil
from bes.fs import file_path, temp_file

class package(object):
  'Class to deal with python packages.'

  @classmethod
  def get_data_program_exe(clazz, program_path, filename, module_name):
    inside_egg, exe_data = clazz._resolve_data(program_path, filename, module_name)
    if not inside_egg:
      if not file_path.is_executable(exe_data):
        raise RuntimeError('not an executable program: %s' % (exe_data))
      return exe_data
    exe_tmp = temp_file.make_temp_file(content = exe_data, prefix = path.basename(program_path) + '-')
    os.chmod(exe_tmp, 0o755)
    return exe_tmp

  @classmethod
  def is_inside_egg(clazz, data_path, filename, module_name):
    inside_egg, _ = clazz._resolve_data(data_path, filename, module_name)
    return inside_egg
  
  @classmethod
  def _resolve_data(clazz, data_path, filename, module_name):
    if path.isabs(data_path):
      raise ValueError('data_path should be relative instead of absolute: %s' % (data_path))
    data_path_abs = path.normpath(path.join(path.dirname(filename), data_path))
    if path.exists(data_path_abs):
      return False, data_path_abs
    print('module_name=%s; data_path=%s' % (module_name, data_path))
    data = pkgutil.get_data(module_name, data_path)
    if not data:
      raise RuntimeError('data for data_path \"%s\" not found in module_name \"%s\"' % (data_path, module_name))
    return True, data
