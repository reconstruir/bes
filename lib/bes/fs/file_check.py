#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from ..system.check import check

from .file_symlink import file_symlink

class file_check(object):

  @classmethod
  def check_file(clazz, filename, exception_class = None, allow_none = False):
    check.check_string(filename, allow_none = allow_none)
    check.check_class(exception_class, allow_none = True)

    exception_class = exception_class or IOError
    filename = clazz._check_symlink(filename, exception_class, allow_none)
    
    if allow_none and filename == None:
      return None
    if not path.exists(filename):
      raise exception_class(f'File not found: {filename}')
    if not path.isfile(filename):
      raise exception_class(f'Not a file: {filename}')
    return path.abspath(filename)

  @classmethod
  def check_dir(clazz, dirname, exception_class = None, allow_none = False):
    check.check_string(dirname, allow_none = allow_none)
    check.check_class(exception_class, allow_none = True)

    exception_class = exception_class or IOError
    dirname = clazz._check_symlink(dirname, exception_class, allow_none)

    if allow_none and dirname == None:
      return None
    if not path.exists(dirname):
      raise exception_class(f'Directory not found: {dirname}')
    if not path.isdir(dirname):
      raise exception_class(f'Not a directory: {dirname}')
    return path.abspath(dirname)

  @classmethod
  def check_file_seq(clazz, files, exception_class = None):
    check.check_string_seq(files)
    check.check_class(exception_class, allow_none = True)

    result = []
    for filename in files:
      result.append(clazz.check_file(filename, exception_class = exception_class))
    return result
  
  @classmethod
  def check_dir_seq(clazz, dirs, exception_class = None, ignore_files = False):
    check.check_string_seq(dirs)
    check.check_class(exception_class, allow_none = True)

    result = []
    for d in dirs:
      should_ignore = ignore_files and path.isfile(d)
      if not should_ignore:
        result.append(clazz.check_dir(d, exception_class = exception_class))
    return result

  @classmethod
  def check_file_or_dir(clazz, ford, exception_class = None, allow_none = False):
    check.check_string(ford, allow_none = allow_none)
    check.check_class(exception_class, allow_none = True)

    exception_class = exception_class or IOError
    ford = clazz._check_symlink(ford, exception_class, allow_none)

    if allow_none and ford == None:
      return None
    if not path.exists(ford):
      raise exception_class(f'File not found: {ford}')
    if not (path.isfile(ford) or path.isdir(ford)):
      raise exception_class(f'Not a file or directory: {ford}')
    return path.abspath(ford)

  @classmethod
  def check_file_or_dir_seq(clazz, fords, exception_class = None):
    check.check_string_seq(fords)
    check.check_class(exception_class, allow_none = True)

    result = []
    for f in fords:
      result.append(clazz.check_file_or_dir(f, exception_class = exception_class))
    return result
  
  @classmethod
  def _check_symlink(clazz, filename, exception_class, allow_none):
    if allow_none and filename == None:
      return None
    if not path.islink(filename):
      return filename
    if file_symlink.is_broken(filename):
      raise exception_class(f'Broken symlink: {filename}')
    return file_symlink.resolve(filename)
