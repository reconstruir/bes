#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import glob
from os import path

from ..common.algorithm import algorithm
from ..common.object_util import object_util
from ..system.check import check

class bf_glob(object):
  'bf_glob'
  
  @classmethod
  def glob(clazz, paths, patterns):
    'Like glob but handles one or more paths and one or more patterns'
    patterns = object_util.listify(patterns)
    result = []
    for pattern in patterns:
      result.extend(clazz._glob_one_pattern(paths, pattern))
    return sorted(algorithm.unique(result))

  @classmethod
  def _glob_one_pattern(clazz, paths, pattern):
    paths = object_util.listify(paths)
    paths = [ path.join(p, pattern) for p in paths ]
    result = []
    for p in paths:
      result.extend(glob.glob(p))
    return sorted(algorithm.unique(result))
  
  _GLOB_CHARS = { '*', '?', '[', ']' }
  @classmethod
  def has_glob_pattern(clazz, filename):
    'Return True if filename has any glob character pattern.'
    check.check_string(filename)
    
    for c in filename:
      if c in clazz._GLOB_CHARS:
        return True
    return False

  @classmethod
  def glob_paths(clazz, paths):
    'Glob a list of paths if needed'
    paths = object_util.listify(paths)
    result = []
    for p in paths:
      if clazz.has_glob_pattern(p):
        result.extend(glob.glob(p))
      else:
        result.append(p)
    return sorted(algorithm.unique(result))
