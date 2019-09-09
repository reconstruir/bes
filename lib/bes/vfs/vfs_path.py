#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
from collections import namedtuple

class vfs_path(object):
  'Class to deal with vfs paths.'

  # vfs paths are use unix style regardless of the python runtime platform
  SEP = '/'

  @classmethod
  def join(clazz, *parts):
    'Same as path.join()'
    return clazz.SEP.join(parts)

  @classmethod
  def split(clazz, filename):
    'Same as path.split()'
    return filename.split(clazz.SEP)

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
    leading = leading and filename.startswith(clazz.SEP)
    trailing = trailing and filename.endswith(clazz.SEP)
    if not leading and not trailing:
      return filename
    start = 0
    end = len(filename)
    if leading:
      start = len(clazz.SEP)
    if trailing:
      end = -len(clazz.SEP)
    return filename[start:end]

  @classmethod
  def ensure_rsep(clazz, filename):
    'Ensure that the given filename has a trailing separator.'
    if not filename.endswith(clazz.SEP):
      return filename + clazz.SEP
    return filename

  @classmethod
  def ensure_lsep(clazz, filename):
    'Ensure that the given filename has a leading separator.'
    if not filename.startswith(clazz.SEP):
      return clazz.SEP + filename
    return filename

  @classmethod
  def ends_with_sep(clazz, filename):
    'Return True if filename ends with a separator.'
    return filename.endswith(clazz.SEP)

  @classmethod
  def starts_with_sep(clazz, filename):
    'Return True if filename starts with a separator.'
    return filename.startswith(clazz.SEP)

  @classmethod
  def basename(clazz, filename):
    'Same as path.basename()'
    if filename in [ '', clazz.SEP ]:
      return ''
    parts = clazz.split(filename)
    return parts[-1]
  
  @classmethod
  def dirname(clazz, filename):
    'Same as path.dirname()'
    if filename in [ '' ]:
      return ''
    if filename in [ clazz.SEP ]:
      return clazz.SEP
    filename = clazz.rstrip_sep(filename)
    parts = clazz.split(filename)[0:-1]
    if parts in [ [ '']  ]:
      return '/'
    return clazz.join(*parts)

  _sprit_basename_rv = namedtuple('_sprit_basename_rv', 'dirname, basename')
  @classmethod
  def split_basename(clazz, filename):
    return clazz._sprit_basename_rv(clazz.dirname(filename),
                                    clazz.basename(filename))

  @classmethod
  def dedup_sep(clazz, filename):
    'Dedup separators in a vfs_path'
    pattern = r'{}{{2,}}'.format(clazz.SEP)
    return re.sub(pattern, clazz.SEP, filename, flags = re.DOTALL)
  
  @classmethod
  def normalize(clazz, filename):
    '''
    Normalize a vfs path including:
    - dedup separators: //foo///bar/// => /foo/bar/
    - ensure leading separator
    '''
    deduped = clazz.dedup_sep(filename)
    normalized = clazz.ensure_lsep(deduped)
    return normalized
