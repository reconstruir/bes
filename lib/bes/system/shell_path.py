#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from os import path

from .check import check
from .log import logger

class shell_path(object):
  'Class to deal with shell paths like PATH and PYTHONPATH'

  _log = logger('shell_path')
  
  @classmethod
  def split(clazz, p):
    'Split a path.'
    check.check_string(p, allow_none = True)
    
    if p in ( None, '' ):
      return []
    return p.split(path.pathsep)

  @classmethod
  def join(clazz, parts):
    'Join a path.'
    check.check_seq(parts, check.STRING_TYPES)
    
    return path.pathsep.join(parts)

  @classmethod
  def remove_duplicates(clazz, p):
    check.check_string(p)

    if p == '':
      return p
    parts = clazz.split(p)
    unique_parts = clazz.unique_parts(parts)
    return clazz.join(unique_parts)

  @classmethod
  def unique_parts(clazz, parts):
    check.check_list(parts)

    seen = {}
    unique_parts = [ seen.setdefault(x, x) for x in parts if x not in seen ]
    return [ x for x in unique_parts if x ]

  @classmethod
  def normalize(clazz, p):
    check.check_string(p)

    if p == '':
      return p
    parts = clazz.split(p)
    nparts = clazz.normalize_parts(parts)
    return clazz.join(nparts)

  @classmethod
  def resolve(clazz, value):
    if check.is_string(value):
      return value
    if check.is_seq(value):
      for part in value:
        if not check.is_string(part):
          raise TypeError(f'part should be string instead of {type(part).__name__}: {part}')
      return clazz.join(value)
    raise TypeError(f'value should be string or string sequence instead of {type(part).__name__}: {value}')

  @classmethod
  def resolve_parts(clazz, value):
    if check.is_string(value):
      return clazz.split(value)
    if check.is_seq(value):
      for part in value:
        if not check.is_string(part):
          raise TypeError(f'part should be string instead of {type(part).__name__}: {part}')
      return value
    raise TypeError(f'value should be string or string sequence instead of {type(part).__name__}: {value}')
  
  @classmethod
  def normalize_parts(clazz, parts):
    check.check_list(parts)

    result = []
    for part in parts:
      npart = clazz.normalize_part(part)
      if npart:
        result.append(npart)
    return result

  @classmethod
  def remove(clazz, p, remove_p):
    parts = clazz.resolve_parts(p)
    remove_parts = clazz.resolve_parts(remove_p)
    new_parts = clazz.remove_parts(parts, remove_parts)
    return clazz.join(new_parts)

  @classmethod
  def remove_parts(clazz, parts, remove_parts):
    clazz.check_parts(parts)
    clazz.check_parts(remove_parts)
    
    remove_set = set(remove_parts)
    return [ part for part in parts if part not in remove_set ]
  
  @classmethod
  def append(clazz, p1, p2):
    parts1 = clazz.resolve_parts(p1)
    parts2 = clazz.resolve_parts(p2)

    new_parts1 = clazz.remove_parts(parts1, parts2)
    new_parts = new_parts1 + parts2
    return clazz.join(new_parts)

  @classmethod
  def prepend(clazz, p1, p2):
    parts1 = clazz.resolve_parts(p1)
    parts2 = clazz.resolve_parts(p2)

    new_parts1 = clazz.remove_parts(parts1, parts2)
    new_parts = parts2 + new_parts1
    return clazz.join(new_parts)
  
  @classmethod
  def normalize_part(clazz, part):
    check.check_string(part)

    if part in ( '', None ):
      return None
    result = path.normpath(part)
    count = clazz._count_leading_sep(result)
    if count > 1:
      result = result[count - 1:]
    return result

  @classmethod
  def _count_leading_sep(clazz, part):
    count = 0
    for c in part:
      if c == path.sep:
        count += 1
      else:
        break
    return count
      
  _diff_result = namedtuple('_diff_result', 'appended, prepended, removed')
  @classmethod
  def diff(clazz, p1, p2):
    check.check_string(p1)
    check.check_string(p2)

    n1 = clazz.normalize(p1)
    n2 = clazz.normalize(p2)
    
    clazz._log.log_d(f'shell_path.diff: p1="{p1}" p2="{p2}" n1="{n1}" n2="{n2}"')

    if n1 in n2:
      left, delimiter, right = n2.partition(n1)
      nleft = clazz.normalize(left)
      nright = clazz.normalize(right)
      assert delimiter == n1
      clazz._log.log_d(f'shell_path.diff1: nleft="{nleft}" nright="{nright}"')
      appended = clazz.split(nright)
      prepended = clazz.split(nleft)
      removed = []
      clazz._log.log_d(f'shell_path.diff1: appended={appended} prepended={prepended} removed={removed}')
      return clazz._diff_result(appended, prepended, removed)
    
    up1 = clazz.remove_duplicates(p1)
    up2 = clazz.remove_duplicates(p2)

    clazz._log.log_d(f'shell_path.diff2: up1={up1} up2={up2}')
    
    parts1 = clazz.split(up1)
    parts2 = clazz.split(up2)

    for i, p in enumerate(parts1):
      clazz._log.log_d(f'shell_path.diff2: parts1: {i}: {p}')

    for i, p in enumerate(parts2):
      clazz._log.log_d(f'shell_path.diff2: parts2: {i}: {p}')

    set1 = set(parts1)
    set2 = set(parts2)
    appended = [ part for part in parts2 if not part in set1 ]
    prepended = []
    removed = [ part for part in parts1 if not part in set2 ]
    clazz._log.log_d(f'shell_path.diff2: appended={appended} prepended={prepended} removed={removed}')
    return clazz._diff_result(appended, prepended, removed)

  @classmethod
  def check_parts(clazz, parts):
    if not check.is_seq(parts):
      raise TypeError(f'parts should be a string sequence instead of {type(parts).__name__}: {parts}')
      
    for i, part in enumerate(parts, start = 1):
      if not check.is_string(part):
        raise TypeError(f'part {i} type should be string instead of {type(part).__name__}: {part}')
