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
    
    if p == None:
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
  
  _diff_result = namedtuple('_diff_result', 'added, removed')
  @classmethod
  def diff(clazz, p1, p2):
    check.check_string(p1)
    check.check_string(p2)

    up1 = clazz.remove_duplicates(p1)
    up2 = clazz.remove_duplicates(p2)

    clazz._log.log_d(f'shell_path.diff: up1={up1} up2={up2}')
    
    parts1 = clazz.split(up1)
    parts2 = clazz.split(up2)

    for i, p in enumerate(parts1):
      clazz._log.log_d(f'shell_path.diff: parts1: {i}: {p}')

    for i, p in enumerate(parts2):
      clazz._log.log_d(f'shell_path.diff: parts2: {i}: {p}')

    set1 = set(parts1)
    set2 = set(parts2)
    added = [ part for part in parts2 if not part in set1 ]
    removed = [ part for part in parts1 if not part in set2 ]
    clazz._log.log_d(f'shell_path.diff: added={added} removed={removed}')
    return clazz._diff_result(added, removed)
