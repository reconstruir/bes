#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import fnmatch, re, os.path as path

from bes.common.algorithm import algorithm
from bes.common.object_util import object_util

class file_match(object):

  ANY = 1
  NONE = 2
  ALL = 3

  VALID_TYPES = [ ANY, NONE, ALL ]

  @classmethod
  def match_type_is_valid(clazz, match_type):
    return match_type in clazz.VALID_TYPES

  @classmethod
  def _match(clazz, filenames, patterns, match_func, match_type, basename = True):
    '''
    Match a list of files with patterns using match_func and match_type.
    match_func should be the form match_func(filename, patterns)
    '''
    
    assert clazz.match_type_is_valid(match_type)

    filenames = object_util.listify(filenames)
    patterns = object_util.listify(patterns) # or [])
    result = []

    if not patterns:
      if match_type == clazz.ANY:
        return []
      elif match_type == clazz.NONE:
        return filenames
      elif match_type == clazz.ALL:
        return []

    func_map = {
      clazz.ANY: clazz._match_any,
      clazz.NONE: clazz._match_none,
      clazz.ALL: clazz._match_all,
    }

    func = func_map[match_type]

    result = []
    for filename in filenames:
      if basename:
        filename_for_match = path.basename(filename)
      else:
        filename_for_match = filename
      if func(match_func, filename_for_match, patterns):
        result.append(filename)
    return sorted(algorithm.unique(result))

  @staticmethod
  def _match_any(match_func, filename, patterns):
    for pattern in patterns:
      if match_func(filename, pattern):
        return True
    return False

  @staticmethod
  def _match_all(match_func, filename, patterns):
    for pattern in patterns:
      if not match_func(filename, pattern):
        return False
    return True

  @staticmethod
  def _match_none(match_func, filename, patterns):
    for pattern in patterns:
      if match_func(filename, pattern):
        return False
    return True

  @classmethod
  def match_fnmatch(clazz, filenames, patterns, match_type, basename = True):
    return clazz._match(filenames, patterns, fnmatch.fnmatch, match_type, basename = basename)

  @classmethod
  def match_re(clazz, filenames, expressions, match_type, basename = True):
    expressions = [ re.compile(expression) for expression in expressions ]
    def _match_re(filename, expression):
      return len(expression.findall(filename)) > 0
    return clazz._match(filenames, expressions, _match_re, match_type, basename = basename)

  @classmethod
  def match_function(clazz, filenames, function):
    return [ f for f in filenames if function(f) ]
