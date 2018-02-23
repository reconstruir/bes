#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, os
from bes.common import algorithm, string_util
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

    fpath, fname = path.split(program)
    if fpath:
      if file_path.is_executable(program):
        return program
    else:
      for p in os.environ['PATH'].split(os.pathsep):
        exe_file = path.join(p, program)
        if file_path.is_executable(exe_file):
          return exe_file
    if raise_error:
      raise RuntimeError('Executable for %s not found.  Fix your PATH.' % (program))
    return None

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
