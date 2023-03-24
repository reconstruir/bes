#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path
import datetime

from ..system.check import check

from .match.bf_match import bf_match
from .match.bf_match_options import bf_match_options
from .bfile_filename import bfile_filename
from .bfile_check import bfile_check
from .bfile_entry import bfile_entry
from .bfile_entry_list import bfile_entry_list
from .bfile_path_type import bfile_path_type

class bfile_dir(object):
    
  @classmethod
  def is_empty(clazz, d):
    for entry in os.scandir(d):
      return False
    return True

  @classmethod
  def list(clazz, where, relative = False, file_match = None, options = None):
    'Return a list of where contents.  Returns absolute paths unless relative is True.'
    where = bfile_check.check_dir(where)
    check.check_bool(relative)
    file_match = check.check_bf_match(file_match, allow_none = True, default_value_class = bf_match)
    options = check.check_bf_match_options(options, allow_none = True, default_value_class = bf_match_options)

    entries = bfile_entry_list.listdir(where)
    matched_entries = file_match.match_entries(entries, options = options)
    if relative:
      return matched_entries.as_relative_list(where + path.sep)
    return matched_entries

  @classmethod
  def list_dirs(clazz, where, relative = False, patterns = None, path_type = 'basename'):
    'Like list() but only returns dirs only.'
    where = bfile_check.check_dir(where)
    check.check_bool(relative)
    patterns = check.check_string_seq(patterns, allow_none = True, default_value = [])
    path_type = check.check_bfile_path_type(path_type)
    
    match = bf_match(patterns = patterns)
    match.add_matcher_callable(path.isdir)
    options = bf_match_options(path_type = path_type)
    return clazz.list(where, relative = relative, file_match = match, options = options)

  @classmethod
  def list_files(clazz, where, relative = False, patterns = None, basename = False):
    'Like list() but only returns files.'
    match = bf_match(patterns = patterns)
    match.add_matcher_callable(path.isfile)
    options = bf_match_options(path_type = path_type)
    return clazz.list(where, relative = relative, file_match = match, options = options)
  
  @classmethod
  def empty_dirs(clazz, where):
    match = bf_match(patterns = patterns)
    match.add_matcher_callable(path.isdir)
    match.add_matcher_callable(clazz.is_empty)
    return clazz.list(where, relative = relative, file_match = match)

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
      raise ValueError(f'Not a directory: "{d}"')
    if not path.exists(d):
      raise ValueError(f'Directory does not exist: "{d}"')
    os.rmdir(d)
