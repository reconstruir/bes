#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import fnmatch, re, os.path as path

from bes.common.algorithm import algorithm
from bes.common.object_util import object_util

from .bfile_filename_match_type import bfile_filename_match_type

class bfile_filename_matcher(object):

  @classmethod
  def match_type_is_valid(clazz, match_type):
    return bfile_filename_match_type.is_valid(match_type)

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
      if match_type == bfile_filename_match_type.ANY:
        return []
      elif match_type == bfile_filename_match_type.NONE:
        return filenames
      elif match_type == bfile_filename_match_type.ALL:
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
  def match_fnmatch(clazz, filenames, patterns, match_type = None, basename = True):
    patterns = object_util.listify(patterns)
    match_type = match_type or clazz.ANY
    return clazz._match(filenames, patterns, fnmatch.fnmatch, match_type, basename = basename)

  @classmethod
  def match_re(clazz, filenames, expressions, match_type = None, basename = True):
    expressions = object_util.listify(expressions)
    match_type = match_type or clazz.ANY
    expressions = [ re.compile(expression) for expression in expressions ]
    def _match_re(filename, expression):
      return len(expression.findall(filename)) > 0
    return clazz._match(filenames, expressions, _match_re, match_type, basename = basename)

  @classmethod
  def match_function(clazz, filenames, function, match_type = None, basename = True):
    match_type = match_type or clazz.ANY
    assert clazz.match_type_is_valid(match_type)
    filenames = object_util.listify(filenames)
    result = []
    for filename in filenames:
      if basename:
        filename_for_match = path.basename(filename)
      else:
        filename_for_match = filename
      if clazz._match_function_one(filename_for_match, function, match_type):
        result.append(filename)
    return sorted(algorithm.unique(result))

  @classmethod
  def _match_function_one(clazz, filename, function, match_type):
    if match_type in [ clazz.ANY, clazz.ALL ]:
      return function(filename)
    elif match_type == clazz.NONE:
      return not function(filename)
    else:
      assert False
