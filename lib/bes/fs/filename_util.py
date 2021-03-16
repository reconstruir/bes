#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.common.check import check
from bes.system.host import host

class filename_util(object):
  'Class to deal with file names'

  @classmethod
  def extension(clazz, filename):
    'Return the extension for filename.'
    check.check_string(filename)

    _, ext = path.splitext(filename)
    if ext == '':
      return None
    assert ext[0] == os.extsep
    return ext[1:]
  
  @classmethod
  def has_extension(clazz, filename, extension):
    'Return True if filename has extension.'
    check.check_string(filename)
    check.check_string(extension)
    
    return clazz.extension(filename) == extension
  
  @classmethod
  def has_any_extension(clazz, filename, extensions):
    check.check_string(filename)
    check.check_string_seq(extensions)

    return clazz.extension(filename) in set(extensions)

  @classmethod
  def xp_filename(clazz, p, sep = None):
    if host.is_windows():
      return clazz._xp_filename_windows(p, sep = sep)
    elif host.is_unix():
      return clazz._xp_filename_unix(p, sep = sep)
    else:
      host.raise_unsupported_system()

  @classmethod
  def native_filename(clazz, p):
    return clazz.xp_filename(p, sep = os.sep)
      
  @classmethod
  def xp_filename_list(clazz, l, sep = None):
    if l == None:
      return None
    assert isinstance(l, list)
    return [ clazz.xp_filename(n, sep = sep) for n in l ]

  @classmethod
  def native_filename_list(clazz, l):
    return clazz.xp_filename_list(l, sep = os.sep)
      
  _XP_SEP = '/'
  @classmethod
  def _xp_filename_windows(clazz, p, sep = None):
    sep = sep or clazz._XP_SEP
    _, split_path = path.splitdrive(p)
    xp_split_path = split_path.replace('\\', sep)
    xp_split_path = xp_split_path.replace('/', sep)
    result = p.replace(split_path, xp_split_path)
    return result
  
  @classmethod
  def _xp_filename_unix(clazz, p, sep = None):
    sep = sep or clazz._XP_SEP
    result = p.replace('/', sep)
    result = result.replace('\\', sep)
    return result
  
