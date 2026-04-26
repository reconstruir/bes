#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path
import datetime

from ..system.check import check

from .bf_check import bf_check
from .bf_entry import bf_entry
from .bf_entry_list import bf_entry_list
from .bf_filename import bf_filename
from .bf_path_type import bf_path_type

from .match.bf_file_matcher import bf_file_matcher
from .match.bf_file_matcher_mode import bf_file_matcher_mode

class bf_dir(object):
    
  @classmethod
  def is_empty(clazz, d):
    for entry in os.scandir(d):
      return False
    return True

  @classmethod
  def list(clazz, where, relative = False, matcher = None, match_type = None):
    'Return a list of where contents.'
    where = bf_check.check_dir(where)
    check.check_bool(relative)
    matcher = check.check_bf_file_matcher(matcher, allow_none = True)
    match_type = check.check_bf_file_matcher_mode(match_type, allow_none = True)

    entries = bf_entry_list.listdir(where)
    if matcher:
      matched_entries = matcher.match_entries(entries, match_type = match_type)
    else:
      matched_entries = entries
    if relative:
      result = matched_entries.relative_filenames(False)
    else:
      result = matched_entries.absolute_filenames(False)
    return result

  @classmethod
  def list_with_callable(clazz, where, func, relative = False):
    'Return a list of where contents matched by func.'
    where = bf_check.check_dir(where)
    check.check_bool(relative)
    check.check_callable(func)

    matcher = bf_file_matcher()
    matcher.add_item_callable(func, path_type = bf_path_type.ABSOLUTE)
    return clazz.list(where,
                      relative = relative,
                      matcher = matcher,
                      match_type = bf_file_matcher_mode.ALL)
  
  @classmethod
  def list_dirs(clazz, where, relative = False, patterns = None):
    'Like list() but only returns dirs.'
    func = lambda filename: path.isdir(filename)
    return clazz._do_list_files(where, func, relative, patterns)
  
  @classmethod
  def list_files(clazz, where, relative = False, patterns = None):
    'Like list() but only returns files.'
    func = lambda filename: path.isfile(filename)
    return clazz._do_list_files(where, func, relative, patterns)

  @classmethod
  def _do_list_files(clazz, where, func, relative, patterns):
    'Like list() but only returns files.'
    where = bf_check.check_dir(where)
    check.check_bool(relative)
    check.check_callable(func)
    patterns = check.check_string_seq(patterns, allow_none = True)

    matcher = bf_file_matcher()
    matcher.add_item_callable(func, path_type = bf_path_type.ABSOLUTE)
    if patterns:
      matcher.add_item_fnmatch_list(patterns, path_type = bf_path_type.BASENAME)
    return clazz.list(where,
                      relative = relative,
                      matcher = matcher,
                      match_type = bf_file_matcher_mode.ALL)
  
  @classmethod
  def empty_dirs(clazz, where):
    matcher = bf_file_matcher(patterns = patterns)
    matcher.add_item_callable(path.isdir)
    matcher.add_item_callable(clazz.is_empty)
    return clazz.list(where, relative = relative, matcher = matcher)

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
