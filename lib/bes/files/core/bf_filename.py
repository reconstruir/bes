#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os
import os.path as path

from ..common.char_util import char_util
from ..common.hash_util import hash_util
from ..system.check import check
from ..system.filesystem import filesystem
from ..system.host import host

class bf_filename(object):
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

  @classmethod
  def replace_extension(clazz, filename, new_extension):
    'Replace the extension.'
    check.check_string(filename)
    check.check_string(new_extension)

    old_extension = clazz.extension(filename)
    if not old_extension:
      return filename
    return filename[0:-len(old_extension)] + new_extension
  
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
    count = 0
    for count, c in enumerate(reversed(filename)):
      if not char_util.is_punctuation(c):
        break
    if count == 0:
      return filename
    return filename[0 : -count]

  @classmethod
  def shorten(clazz, basename, max_length = None, include_hash = False, hash_length = None):
    'Shorten a basename preserving the extension'
    check.check_string(basename)
    check.check_int(max_length, allow_none = True)
    check.check_bool(include_hash)
    check.check_int(hash_length, allow_none = True)

    if path.sep in basename:
      raise ValueError(f'filename should be a basename not path: "{basename}"')

    if hash_length != None:
      if hash_length < 8:
        raise ValueError(f'hash_length should be between 8 and 64: "{hash_length}"')
      if hash_length > 64:
        raise ValueError(f'hash_length should be between 8 and 64: "{hash_length}"')
        
    max_length = max_length or filesystem.max_filename_length()

    ext = clazz.extension(basename)
    basename_no_ext = clazz.without_extension(basename)
    len_basename_no_ext = len(basename_no_ext)

    if ext:
      min_needed_ext = len(ext) + len(path.extsep)
    else:
      min_needed_ext = 0
    if min_needed_ext >= max_length:
      raise ValueError(f'extension exceeds max length({max_length}): "{basename}"')
    available = max_length - min_needed_ext + 1
    assert available >= 1
    if available <= len_basename_no_ext:
      hash_sep = '-'
      if include_hash:
        hash_string = hash_util.hash_string_sha256(basename)
        if hash_length != None:
          hash_string = hash_string[0:hash_length]
        hash_part = hash_sep + hash_string
        hash_part_length = len(hash_sep) + hash_length
        if hash_part_length >= available:
          raise ValueError(f'hash would exceed max length({max_length}): "{basename}"')
      else:
        hash_part = ''
        hash_part_length = 0
      len_hash_part = len(hash_part)
      basename_no_ext = basename_no_ext[0:available - 1 - len_hash_part] + hash_part
    return clazz.add_extension(basename_no_ext, ext)

  @classmethod
  def lstrip_sep(clazz, filename):
    'Return the filename without a leading path separator.'
    return clazz._strip_sep(filename, True, False)

  @classmethod
  def rstrip_sep(clazz, filename):
    'Return the filename without a trailing path separator.'
    return clazz._strip_sep(filename, False, True)

  @classmethod
  def strip_sep(clazz, filename):
    'Return the filename without either leading or trailing path separator.'
    return clazz._strip_sep(filename, True, True)

  @classmethod
  def _strip_sep(clazz, filename, leading, trailing):
    'Return the filename without a trailing path separator.'

    leading = leading and filename.startswith(path.sep)
    trailing = trailing and filename.endswith(path.sep)
    if not leading and not trailing:
      return filename
    start = 0
    end = len(filename)
    if leading:
      start = len(path.sep)
    if trailing:
      end = -len(path.sep)
    return filename[start:end]

  @classmethod
  def ensure_rsep(clazz, filename):
    'Ensure that the given filename has a trailing separator.'
    if not filename.endswith(os.sep):
      return filename + os.sep
    return filename

  @classmethod
  def ensure_lsep(clazz, filename):
    'Ensure that the given filename has a leading separator.'
    if not filename.startswith(os.sep):
      return os.sep + filename
    return filename

  @classmethod
  def remove_head(clazz, filename, head):
    'Return filename without head.'
    head = clazz.ensure_rsep(path.normpath(head))
    result = clazz._str_remove_head(filename, head)
    return result

  @classmethod
  def remove_tail(clazz, filename, tail):
    'Return filename without tail.'
    tail = clazz.ensure_lsep(path.normpath(tail))
    result = clazz._str_remove_tail(filename, tail)
    return result

  @classmethod
  def _str_remove_head(clazz, s, head):
    if s.startswith(head):
      return s[len(head):]
    return s

  @classmethod
  def _str_remove_tail(clazz, s, tail):
    if s.endswith(tail):
      return s[0:-len(tail)]
    return s

  @classmethod
  def un_expanduser(clazz, p):
    return p.replace(path.expanduser('~'), '~')

  @classmethod
  def is_basename(clazz, filename):
    return path.basename(filename) == filename
