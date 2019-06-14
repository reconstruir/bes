#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, shutil
import datetime

from .file_match import file_match
from .file_util import file_util
from .tar_util import tar_util

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

  @classmethod
  def older_dirs(clazz, dirs, days = 0, seconds = 0, microseconds = 0,
                 milliseconds = 0, minutes = 0, hours = 0, weeks = 0):
    delta = datetime.timedelta(days = days,
                               seconds = seconds,
                               microseconds = microseconds,
                               milliseconds = milliseconds,
                               minutes = minutes,
                               hours = hours,
                               weeks = weeks)
    now = datetime.datetime.now()
    ago = now - delta
    result = []
    for d in dirs:
      mtime = datetime.datetime.fromtimestamp(os.stat(d).st_mtime)
      if mtime <= ago:
        result.append(d)
    return result

  @classmethod
  def move_files(clazz, src_dir, dst_dir):
    if not path.isdir(src_dir):
      raise IOError('Not a directory: %s' % (src_dir))
    if not path.isdir(dst_dir):
      raise IOError('Not a directory: %s' % (dst_dir))
    if not file_util.same_device_id(src_dir, dst_dir):
      raise IOError('src_dir and dst_dir are not in the same device: %s %s' % (src, dst_dir))
    for f in clazz.list(src_dir, relative = True):
      src_file = path.join(src_dir, f)
      dst_file = path.join(dst_dir, f)
      if path.isdir(src_file):
        if path.exists(dst_file):
          tar_util.copy_tree(src_file, dst_file)
          file_util.remove(src_file)
        else:
          shutil.move(src_file, dst_file)
      else:
        os.rename(src_file, dst_file)
