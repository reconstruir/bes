#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, pkgutil, sys
from bes.files.bf_path import bf_path
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file

from ..files.bf_entry import bf_entry

class package(object):
  'Class to deal with python packages.'

  @classmethod
  def get_data_program_exe(clazz, program_path, filename, module_name):
    try:
      inside_egg, exe_data = clazz._resolve_data(program_path, filename, module_name)
      if not inside_egg:
        if not bf_entry(exe_data).is_executable:
          return None
        return exe_data
      exe_tmp = temp_file.make_temp_file(content = exe_data, prefix = path.basename(program_path) + '-')
      os.chmod(exe_tmp, 0o755)
      return exe_tmp
    except Exception as ex:
      return None

  @classmethod
  def get_data_content(clazz, data_path, filename, module_name):
    try:
      print('data_path=%s, filename=%s, module_name=%s' % (data_path, filename, module_name))
      inside_egg, data = clazz._resolve_data(data_path, filename, module_name)
      print('inside_egg=%s, data=%s' % (inside_egg, data))
      if not inside_egg:
        if not path.isfile(data):
          raise RuntimeError('Not a file: %s' % (data))
        result = file_util.read(data)
        if not result:
          raise RuntimeError('Failed to read: %s' % (data))
        return result
      return data
    except Exception as ex:
      sys.stderr.write('package: caught exception: %s\n' % (str(ex)))
      sys.stdout.flush()
      return None
    
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
    data = pkgutil.get_data(module_name, data_path)
    if not data:
      raise RuntimeError('data for data_path \"%s\" not found in module_name \"%s\"' % (data_path, module_name))
    return True, data
