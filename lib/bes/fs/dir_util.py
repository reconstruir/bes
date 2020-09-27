#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, shutil
import datetime

from .file_match import file_match
from .file_util import file_util

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
  def remove(clazz, d):
    if path.isfile(d):
      raise ValueError('Not a directory: "{}"'.format(d))
    if not path.exists(d):
      raise ValueError('Directory does not exits: "{}"'.format(d))
    os.rmdir(d)
