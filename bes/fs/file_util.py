#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path as path, os, platform, shutil, tempfile
from bes.common import object_util, Shell, string_util
from bes.system import log

from collections import namedtuple

class file_util(object):

  @classmethod
  def mkdir(clazz, p):
    if path.isdir(p):
      return
    os.makedirs(p)
                  
  @classmethod
  def remove(clazz, files):
    files = object_util.listify(files)
    for f in files:
      try:
        if path.isdir(f):
          shutil.rmtree(f)
        else:
          os.remove(f)
      except Exception, ex:
        clazz.log_d('Caught exception %s removing %s' % (ex, f))
        pass

  @classmethod
  def save(clazz, filename, content = None, mode = None):
    'Atomically save content to filename using an intermediate temporary file.'
    dirname, basename = os.path.split(filename)
    clazz.mkdir(path.dirname(filename))
    tmp = tempfile.NamedTemporaryFile(prefix = basename, dir = dirname, delete = False, mode = 'w')
    if content:
      tmp.write(content)
    tmp.flush()
    os.fsync(tmp.fileno())
    tmp.close()
    if mode:
      os.chmod(tmp.name, mode)
    os.rename(tmp.name, filename)
    return filename

  @classmethod
  def backup(clazz, filename, suffix = '.bak'):
    'Make a backup of filename if it exists.'
    if path.exists(filename):
      if path.isfile(filename):
        clazz.copy(filename, filename + suffix)
      else:
        raise RuntimeError('Not a file: %s' % (filename))

  @classmethod
  def symlink(clazz, src, dst):
    clazz.remove(dst)
    os.symlink(src, dst)

  @classmethod
  def extension(clazz, filename):
    'Return the extension for filename.'
    return string_util.remove_head(path.splitext(filename)[1], os.extsep)

  @classmethod
  def remove_extension(clazz, filename):
    'Return the root of filename withouth extension.'
    return path.splitext(filename)[0]

  @classmethod
  def lstrip_sep(clazz, filename):
    'Return the filename without a leading path separator.'
    return clazz.__strip_sep(filename, True, False)

  @classmethod
  def rstrip_sep(clazz, filename):
    'Return the filename without a trailing path separator.'
    return clazz.__strip_sep(filename, False, True)

  @classmethod
  def strip_sep(clazz, filename):
    'Return the filename without either leading or trailing path separator.'
    return clazz.__strip_sep(filename, True, True)

  @classmethod
  def __strip_sep(clazz, filename, leading, trailing):
    'Return the filename without a trailing path separator.'

    leading = leading and filename.startswith(path.sep)
    trailing = trailing and filename.endswith(path.sep)
    if not leading and not trailing:
      return filename
    start = 0
    end = len(filename)
    if leading:
      start = len(path.sep)
    if trailing:
      end = -len(path.sep)
    return filename[start:end]

  @classmethod
  def ensure_rsep(clazz, filename):
    'Ensure that the given filename has a trailing separator.'
    if not filename.endswith(os.sep):
      return filename + os.sep
    return filename

  @classmethod
  def ensure_lsep(clazz, filename):
    'Ensure that the given filename has a leading separator.'
    if not filename.startswith(os.sep):
      return os.sep + filename
    return filename

  @classmethod
  def remove_head(clazz, filename, head):
    'Return filename without head.'
    head = clazz.ensure_rsep(path.normpath(head))
    result = string_util.remove_head(filename, head)
    return result

  @classmethod
  def remove_tail(clazz, filename, tail):
    'Return filename without tail.'
    tail = clazz.ensure_lsep(path.normpath(tail))
    result = string_util.remove_tail(filename, tail)
    return result

  @classmethod
  def rename(clazz, src, dst):
    clazz.mkdir(path.dirname(dst))
    shutil.move(src, dst)

  @classmethod
  def copy(clazz, src, dst):
    clazz.mkdir(path.dirname(dst))
    shutil.copy(src, dst)

  @classmethod
  def mode(clazz, filename):
    'Return only the lower bits of a inode mode (permissions)'
    return os.stat(filename).st_mode & 0777

  @classmethod
  def size(clazz, filename):
    return os.stat(filename).st_size

  @classmethod
  def copy_mode(clazz, src, dst):
    shutil.copymode(src, dst)

  @classmethod
  def copy_mode(clazz, src, dst):
    shutil.copymode(src, dst)
    
  @classmethod
  def read(clazz, filename):
    'Read a file into a string.'
    with open(filename, 'rb') as f:
      return f.read()

  @classmethod
  def read_as_lines(clazz, filename, ignore_empty = True):
    'Read a file as a list of lines.'
    lines = clazz.read(filename).split('\n')
    if ignore_empty:
      return [ line for line in lines if line ]
    else:
      return lines
      
  @classmethod
  def make_paths_absolute(clazz, paths):
    paths = object_util.listify(paths)
    return [ clazz.ensure_abspath(p) for p in paths ]

  @classmethod
  def ensure_abspath(clazz, p):
    assert p
    if path.isabs(p):
      return p
    return path.abspath(p)

log.add_logging(file_util, 'file_util')
