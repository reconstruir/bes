#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, os.path as path

from .file_match import file_match

class dir_util(object):
    
  @classmethod
  def is_empty(clazz, d):
    return clazz.list(d) == []

  @classmethod
  def list(clazz, d, relative = False, patterns = None):
    'Return a list of a d contents.  Returns absolute paths unless relative is True.'
    result = sorted(os.listdir(d))
    if not relative:
      result = [ path.join(d, f) for f in result ]
    if patterns:
      result = file_match.match_fnmatch(result, patterns, file_match.ANY)
    return result

  @classmethod
  def list_dirs(clazz, d):
    'Like list() but only returns dirs.'
    return [ f for f in clazz.list(d, full_path = True) if path.isdir(f) ]

  @classmethod
  def empty_dirs(clazz, d):
    return [ f for f in clazz.list_dirs(d) if clazz.is_empty(f) ]

  @classmethod
  def all_parents(clazz, d):
    result = []
    while True:
      parent = path.dirname(d)
      result.append(parent)
      if parent == '/':
        break
      d = parent
    return sorted(result)
