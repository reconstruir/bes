#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os
import os.path as path

from bes.common.char_util import char_util
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
  def has_extension(clazz, filename, extension, ignore_case = False):
    'Return True if filename has extension.'
    check.check_string(filename)
    check.check_string(extension)

    if ignore_case:
      filename = filename.lower()
      extension = extension.lower()
    return clazz.extension(filename) == extension
  
  @classmethod
  def has_any_extension(clazz, filename, extensions, ignore_case = False):
    check.check_string(filename)
    check.check_string_seq(extensions)

    ext = clazz.extension(filename)
    if ext == None:
      return False
    if ignore_case:
      ext = ext.lower()
      extensions = [ e.lower() for e in extensions ]
    return ext in set(extensions)

  @classmethod
  def without_extension(clazz, filename):
    'Return the filename without its extension if any.'
    check.check_string(filename)

    left, _ = path.splitext(filename)
    return left

  @classmethod
  def add_extension(clazz, filename, extension):
    'Return the filename with extension.'
    check.check_string(filename)
    check.check_string(extension, allow_none = True)

    if not extension:
      return filename
    return filename + path.extsep + extension
  
  _split_filename = namedtuple('_split_filename', 'root, extension')
  @classmethod
  def split_extension(clazz, filename):
    'Split filename into 2 parts.  extension will be None if not present.'
    check.check_string(filename)

    root = clazz.without_extension(filename)
    extension = clazz.extension(filename)
    return clazz._split_filename(root, extension)
  
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
  
  @classmethod
  def prefix(clazz, filename):
    'Return the prefix before punctuation.  foo-10.txt => foo.'

    for i, c in enumerate(filename):
      if c.isdigit():
        return clazz._rstrip_punctiation(filename[0:i])
    return None

  @classmethod
  def _rstrip_punctiation(clazz, filename):
    for count, c in enumerate(reversed(filename)):
      if not char_util.is_punctuation(c):
        break
    if count == 0:
      return filename
    return filename[0 : -count]
