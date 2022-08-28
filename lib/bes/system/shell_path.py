#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from enum import IntEnum

import difflib
from os import path

from ..common.algorithm import algorithm
from ..system.check import check
from ..system.log import logger

class _shell_path_diff_action(IntEnum):
  APPEND = 1
  PREPEND = 2
  REMOVE = 3
  SET = 4

_shell_path_diff_instruction = namedtuple('_shell_path_diff_instruction', 'action, value')

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
  def join(clazz, p):
    'Join a path.'
    check.check_seq(p, check.STRING_TYPES)
    return path.pathsep.join(p)

  @classmethod
  def remove_duplicates(clazz, p):
    check.check_string(p)

    if p == '':
      return p
    parts = clazz.split(p)
    unique_parts = algorithm.unique(parts)
    return clazz.join(unique_parts)

  @classmethod
  def diff(clazz, p1, p2):
    check.check_string(p1)
    check.check_string(p2)

    up1 = clazz.remove_duplicates(p1)
    up2 = clazz.remove_duplicates(p2)

    if not up1 in up2:
      yield _shell_path_diff_instruction(_shell_path_diff_action.SET, up2)
      return
    
    parts1 = clazz.split(up1)
    parts2 = clazz.split(up2)

    clazz._log.log_d(f'shell_path.diff: parts1={parts1} parts2={parts2}')
    
    sm = difflib.SequenceMatcher(isjunk = None, a = parts1, b = parts2)

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
      clazz._log.log_d(f'shell_path.diff: tag={tag} i1={i1} i2={i2} j1={j1} j2={j2}')
      continue
      if tag == 'insert':
        if i1 == 0:
          for p in reversed(p2[j1:j2]):
            yield instruction(key, p, action.PATH_PREPEND)
        else:
          for p in p2[j1:j2]:
            yield instruction(key, p, action.PATH_APPEND)
      elif tag == 'delete':
        for p in p1[i1:i2]:
          yield instruction(key, p, action.PATH_REMOVE)
      elif tag == 'replace':
        for p in p1[i1:i2]:
          yield instruction(key, p, action.PATH_REMOVE)
        for p in p2[j1:j2]:
          yield instruction(key, p, action.PATH_APPEND)
      else:
        clazz._log.log_e(f'shell_path.diff: unhandled diff tag {tag}')
