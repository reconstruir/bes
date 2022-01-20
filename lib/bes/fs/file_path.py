#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import glob
from os import path
import os
import re

from bes.common.algorithm import algorithm
from bes.common.check import check
from bes.common.object_util import object_util
from bes.common.object_util import object_util
from bes.common.string_util import string_util
from bes.system.os_env import os_env_var
from bes.system.which import which
from bes.text.text_replace import text_replace

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
  def part(clazz, p, index):
    'Return a part of a path by index.'
    v = clazz.split(p)
    return v[index]
  
  @classmethod
  def join(clazz, p):
    'Join a path.'
    assert isinstance(p, list)
    return os.sep.join(p)

  @classmethod
  def replace(clazz, p, src, dst, count = None, backwards = False,
              word_boundary = False, boundary_chars = None):
    'Replace src in path components with dst.'
    check.check_string(p)
    check.check_string(src)
    check.check_string(dst)
    check.check_int(count, allow_none = True)
    check.check_bool(backwards)
    check.check_bool(word_boundary)
    check.check_set(boundary_chars, allow_none = True)
    
    v = clazz.split(p)
    r = range(0, len(v))
    if backwards:
      r = reversed(r)
    if count == None:
      count = len(v)

    current_count = 0
    for i in r:
      part = v[i]
      new_part = text_replace.replace(part, { src: dst },
                                      word_boundary = word_boundary,
                                      boundary_chars = boundary_chars)
      if part != new_part:
        current_count += 1
        if current_count > count:
          break
        v[i] = new_part
    return clazz.join(v)

  @classmethod
  def part_is_valid(clazz, c):
    'Check that a part has only valid basename chars.'
    if path.sep in c:
      return False
    if path.curdir in c:
      return False
    if path.pardir in c:
      return False
    return True
  
  @classmethod
  def check_part(clazz, part):
    'Check that a part has only valid basename chars.'
    if not clazz.part_is_valid(part):
      raise ValueError('Invalid part: "{}"'.format(part))
  
  @classmethod
  def replace_all(clazz, p, src, dst, word_boundary = False, boundary_chars = None):
    'Replace src with dst on all parts of the path.'
    check.check_string(p)
    check.check_string(src)
    check.check_string(dst)
    check.check_bool(word_boundary)
    check.check_set(boundary_chars, allow_none = True)
    
    result = []
    for part in clazz.split(p):
      result.append(text_replace.replace_all(part, src, dst,
                                             word_boundary = word_boundary,
                                             boundary_chars = boundary_chars))
    return clazz.join(result)
  
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
  
#  @classmethod
#  def parent_dir(clazz, p, levels = 1):
#    check.check_string(p)
#    check.check_int(levels)
#
#    if p == path.sep:
#      return None
#    
#    add_sep = ''
#    if p.endswith(path.sep):
#      add_sep = path.sep
#    p = path.normpath(p) + add_sep
#    
#    for i in range(0, levels):
#      dirname = path.dirname(p)
#      if dirname == path.sep:
#        return None
#      parent = path.join(dirname, path.pardir)
#      p = path.normpath(parent)
#    return p

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
  def insert(clazz, p, index, part):
    parts = clazz.split(p)
    parts.insert(index, part)
    return clazz.join(parts)

  @classmethod
  def xp_path_list(clazz, l, pathsep = ':', sep = '/'):
    if l == None:
      return None
    assert isinstance(l, list)
    return [ clazz.xp_path(n) for n in l ]
  
  _access_result = namedtuple('_access_result', 'filename, exists, can_read, can_write, can_execute')
  @classmethod
  def access(clazz, p):
    exists = os.access(p, os.F_OK)
    if exists:
      can_read = os.access(p, os.R_OK)
      can_write = os.access(p, os.W_OK)
      can_execute = os.access(p, os.X_OK)
    else:
      can_read = False
      can_write = False
      can_execute = False
    return clazz._access_result(p, exists, can_read, can_write, can_execute)
