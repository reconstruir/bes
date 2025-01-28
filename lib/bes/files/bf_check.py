#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from ..system.check import check
from ..system.env_var import os_env_var

from .bf_broken_symlink_error import bf_broken_symlink_error
from .bf_not_dir_error import bf_not_dir_error
from .bf_not_file_error import bf_not_file_error
from .bf_permission_error import bf_permission_error
from .bf_symlink import bf_symlink

class bf_check(object):

  #_DISABLED = os_env_var('BES_BF_CHECK_DISABLE').is_set
  
  @classmethod
  def check_file(clazz, filename, allow_none = False):
    check.check_string(filename, allow_none = allow_none)

    #if clazz._DISABLED:
    #  return path.normpath(path.abspath(filename))
    
    if filename:
      filename = path.expanduser(filename)
    filename = clazz._check_symlink(filename, allow_none)
    
    if allow_none and filename == None:
      return None
    if not path.exists(filename):
      raise FileNotFoundError(f'File not found: {filename}')
    if not path.isfile(filename):
      raise bf_not_file_error(f'Not a file: {filename}')
    return path.normpath(path.abspath(filename))

  @classmethod
  def check_dir(clazz, dirname, allow_none = False):
    check.check_string(dirname, allow_none = allow_none)

    #if clazz._DISABLED:
    #  return path.normpath(path.abspath(dirname))
    
    if dirname:
      dirname = path.expanduser(dirname)
    dirname = clazz._check_symlink(dirname, allow_none)

    if allow_none and dirname == None:
      return None
    if not path.exists(dirname):
      raise FileNotFoundError(f'Directory not found: {dirname}')
    if not path.isdir(dirname):
      raise bf_not_dir_error(f'Not a directory: {dirname}')
    return path.normpath(path.abspath(dirname))

  @classmethod
  def check_file_seq(clazz, files):
    check.check_string_seq(files)

    result = []
    for filename in files:
      result.append(clazz.check_file(filename))
    return result
  
  @classmethod
  def check_dir_seq(clazz, dirs, ignore_files = False):
    check.check_string_seq(dirs)

    result = []
    for d in dirs:
      should_ignore = ignore_files and path.isfile(d)
      if not should_ignore:
        result.append(clazz.check_dir(d))
    return result

  @classmethod
  def check_file_or_dir(clazz, ford, allow_none = False):
    check.check_string(ford, allow_none = allow_none)

    #if clazz._DISABLED:
    #  return path.normpath(path.abspath(ford))
    
    if ford:
      ford = path.expanduser(ford)
    ford = clazz._check_symlink(ford, allow_none)

    if allow_none and ford == None:
      return None
    if not path.exists(ford):
      raise FileNotFoundError(f'File not found: {ford}')
    if not (path.isfile(ford) or path.isdir(ford)):
      raise bf_not_file_error(f'Not a file or directory: {ford}')
    return path.normpath(path.abspath(ford))

  @classmethod
  def check_file_or_dir_seq(clazz, fords):
    check.check_string_seq(fords)

    result = []
    for f in fords:
      result.append(clazz.check_file_or_dir(f))
    return result
  
  @classmethod
  def _check_symlink(clazz, filename, allow_none):
    if allow_none and filename == None:
      return None
    if not path.islink(filename):
      return filename
    if bf_symlink.is_broken(filename):
      raise bf_broken_symlink_error(f'Broken symlink: {filename}')
    return bf_symlink.resolve(filename)

  @classmethod
  def check_file_is_readable(clazz, filename):
    'Check that filename is readable and raise a permission error if not.'
    filename = clazz.check_file(filename)

    if not os.access(filename, os.R_OK):
      raise bf_permission_error(f'File is not readable: "{filename}"')

  @classmethod
  def check_file_is_writable(clazz, filename):
    'Check that filename is writable and raise a permission error if not.'
    filename = clazz.check_file(filename)

    if not os.access(filename, os.W_OK):
      raise bf_permission_error(f'File is not writable: "{filename}"')
