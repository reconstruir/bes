#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from ..common.algorithm import algorithm
from ..system.check import check

class shell_path(object):
  'Class to deal with shell paths like PATH and PYTHONPATH'

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
