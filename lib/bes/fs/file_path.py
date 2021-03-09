#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import glob, os.path as path, os, re
from bes.common.check import check
from bes.common.algorithm import algorithm
from bes.common.object_util import object_util
from bes.common.string_util import string_util
from bes.system.which import which
from bes.system.os_env import os_env_var
from bes.common.object_util import object_util

from .file_util import file_util

class file_path(object):
  'file_path'

  @classmethod
  def is_executable(clazz, p):
    'Return True if the path is executable.'
    return path.exists(p) and os.access(p, os.X_OK)

  @classmethod
  def which(clazz, program, raise_error = False):
    'Same as unix which.'
    return which.which(program)

  @classmethod
  def split(clazz, p):
    'Split a path.'
    if not p:
      return []
    if p == '/':
      return [ '' ]
    p = path.normpath(p)
    assert string_util.is_string(p)
    return p.split(os.sep)

  @classmethod
  def join(clazz, p):
    'Join a path.'
    assert isinstance(p, list)
    return os.sep.join(p)

  @classmethod
  def replace(clazz, p, src, dst, count = None, backwards = False):
    'Replace src in path components with dst.'
    v = clazz.split(p)
    r = range(0, len(v))
    if backwards:
      r = reversed(r)
    if count == None:
      count = len(v)

    current_count = 0
    for i in r:
      part = v[i]
      new_part = part.replace(src, dst)
      if part != new_part:
        current_count += 1
        if current_count > count:
          break
        v[i] = new_part
    return clazz.join(v)

  @classmethod
  def depth(clazz, p):
    'Return the depth of p.'
    return len(clazz.split(p))

  @classmethod
  def normalize(clazz, p):
    return path.abspath(path.normpath(p))

  @classmethod
  def parent_dir(clazz, d):
    d = path.normpath(d)
    if d == path.sep:
      return None
    return path.normpath(path.join(d, os.pardir))

  @classmethod
  def common_ancestor(clazz, filenames):
    'Return a common ancestor for all the given filenames or None if there is not one.'
    if not filenames:
      return None

    def _split_filename(f):
      return path.normpath(f).split(os.sep)
    
    if len(filenames) == 1:
      filename_split = _split_filename(filenames[0])
      return os.sep.join(filename_split[0:-1])
    
    split_filenames = [ _split_filename(f) for f in filenames ]
    lengths = [ len(s) for s in split_filenames ]
    min_length = min(lengths)

    levels = [ None ] * min_length
    for i in range(0, min_length):
      levels[i] = set()

    for split_filename in split_filenames:
      for i in range(0, min_length):
        p = split_filename[i]
        save = levels[:]
        levels[i].add(p)

    ancestor_parts = []
    for level in levels:
      if len(level) != 1:
        break
      ancestor_parts.append(level.pop())

    if not ancestor_parts:
      return None
    
    result = os.sep.join(ancestor_parts)
    return result
  
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
  
  @classmethod
  def decompose(clazz, p):
    'Decompose a path into a list of paths starting with the root'
    if not path.isabs(p):
      raise ValueError('path needs to be absolute: %s' % (p))
    if path.ismount(p):
      return []
    result = []
    while True:
      result.append(p)
      p = path.dirname(p)
      if path.ismount(p):
        break
    return [ x for x in reversed(result) ]

  @classmethod
  def normalize_sep(clazz, p, sep = None):
    sep = sep or os.sep
    return path.normpath(sep.join(re.split(r'\\|/', p)))

  @classmethod
  def xp_path(clazz, s, pathsep = ':', sep = '/'):
    result = s.replace(pathsep, os.pathsep)
    result = result.replace(sep, os.sep)
    return result

  @classmethod
  def xp_path_list(clazz, l, pathsep = ':', sep = '/'):
    if l == None:
      return None
    assert isinstance(l, list)
    return [ clazz.xp_path(n) for n in l ]
  
