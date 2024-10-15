#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import os

from datetime import datetime
from collections import namedtuple

from bes.system.check import check
from bes.system.log import logger
from bes.common.object_util import object_util

from ..bf_check import bf_check
from ..bf_entry import bf_entry
from ..bf_entry_list import bf_entry_list
from ..bf_filename import bf_filename
from ..bf_file_type import bf_file_type
from ..bf_path_type import bf_path_type
from ..bf_symlink import bf_symlink
from ..match.bf_file_matcher_type import bf_file_matcher_type
from ..match.bf_file_matcher import bf_file_matcher

from .bf_file_finder_options import bf_file_finder_options
from .bf_file_finder_result import bf_file_finder_result
from .bf_file_finder_stats import bf_file_finder_stats
from .bf_walk import bf_walk

class bf_file_finder(object):

  _log = logger('bf_file_finder')
  
  def __init__(self, options = None):
    check.check_bf_file_finder_options(options, allow_none = True)

    self._options = bf_file_finder_options.clone_or_create(options)
    check.check_bf_file_finder_options(self._options)

  def find_gen(self, where):
    where = bf_check.check_dir_seq(object_util.listify(where))
    for next_where in where:
      for entry in self._find_gen_one_dir(next_where, None):
        yield entry

  def _find_gen_with_stats(self, where, stats_dict):
    where = bf_check.check_dir_seq(object_util.listify(where))
    for next_where in where:
      for entry in self._find_gen_one_dir(next_where, stats_dict):
        yield entry
        
  def _find_gen_one_dir(self, where, stats_dict):
    where = bf_check.check_dir(where)
    where = path.normpath(where)
    result = bf_entry_list()
    where = path.normpath(where)

    self._log.log_d(f'find_gen: where={where} options={self._options}')

    want_files = self._options.file_type.mask_matches(bf_file_type.FILE)
    want_dirs = self._options.file_type.mask_matches(bf_file_type.DIR)
    want_links = self._options.file_type.mask_matches(bf_file_type.LINK)
    count = 0
    done = False
    for item in bf_walk.walk(where,
                             max_depth = self._options.max_depth,
                             follow_links = self._options.follow_links,
                             walk_dir_matcher = self._options.walk_dir_matcher,
                             walk_dir_match_type = self._options.walk_dir_match_type):
      self._log.log_d(f'next: {count + 1}: dirs={item.dirs} files={item.files}')
      if done:
        break
      if stats_dict:
        stats_dict['depth'] = max(stats_dict['depth'], item.depth)
      to_check_files = bf_entry_list()
      to_check_dirs = bf_entry_list()

      if want_files or want_links:
        for next_file_entry in item.files:
          is_link = next_file_entry.is_link
          if want_links and is_link:
            to_check_files.append(next_file_entry)
          if want_files and not is_link:
            to_check_files.append(next_file_entry)

      if want_dirs:
        to_check_dirs += item.dirs

      num_to_check_files = len(to_check_files)
      for i, next_file_entry in enumerate(to_check_files, start = 1):
        if done:
          self._log.log_d(f'done at file|link {i} of {num_to_check_files}: filename={next_file_entry.relative_filename}')
          break
        if self._entry_matches(next_file_entry, where, stats_dict):
          self._log.log_d(f'matched file|link {i} of {num_to_check_files}: filename={next_file_entry.relative_filename}')
          count += 1
          if self._options.found_callback:
            self._options.found_callback(next_file_entry)
          yield next_file_entry
          if self._options.stop_after == count:
            done = True
      matched_dirs = bf_entry_list()
      num_to_check_dirs = len(to_check_dirs)
      for i, next_dir_entry in enumerate(to_check_dirs, start = 1):
        if done:
          self._log.log_d(f'done at dir {i} of {num_to_check_dirs}: filename={next_dir_entry.relative_filename}')
          break
        if self._entry_matches(next_dir_entry, where, stats_dict):
          self._log.log_d(f'matched dir {i} of {num_to_check_dirs}: filename={next_dir_entry.relative_filename}')
          matched_dirs.append(next_dir_entry)
          count += 1
          if self._options.found_callback:
            self._options.found_callback(next_dir_entry)
          yield next_dir_entry
          if self._options.stop_after == count:
            done = True
      self._log.log_d(f'matched_dirs={matched_dirs.basenames()}')
      #dirs[:] = matched_dirs

  def _entry_matches(self, entry, where, stats_dict):
    where_sep_count = where.count(os.sep)
    #print(f'_entry_matches: entry={entry.relative_filename} where={where} where_sep_count={where_sep_count}')
    depth = entry.absolute_filename.count(os.sep) - where_sep_count
    if stats_dict:
      stats_dict['num_checked'] += 1
      if entry.is_dir:
        stats_dict['num_dirs_checked'] += 1
      if entry.is_file:
        stats_dict['num_files_checked'] += 1
    if not self._options.depth_in_range(depth):
      return False
    if self._options.ignore_broken_links and bf_symlink.is_broken(entry.filename):
      return False
    if not self._options.file_matcher_matches(entry):
      return False
    return True
    
  def find_with_stats(self, where):
    stats_dict = {
      'num_checked': 0,
      'num_files_checked': 0,
      'num_dirs_checked': 0,
      'start_time': datetime.now(),
      'end_time': None,
      'depth': 0,
    }
    entries = bf_entry_list()
    for entry in self._find_gen_with_stats(where, stats_dict):
      entries.append(entry)
    stats_dict['end_time'] = datetime.now()
    stats = bf_file_finder_stats(stats_dict['num_checked'],
                                 stats_dict['num_files_checked'],
                                 stats_dict['num_dirs_checked'],
                                 stats_dict['start_time'],
                                 stats_dict['end_time'],
                                 stats_dict['depth'])
    return bf_file_finder_result(entries, stats)

  def find(self, where):
    result = bf_entry_list()
    for entry in self.find_gen(where):
      result.append(entry)
    return result
  
  @classmethod
  def find_with_options(clazz, where, **kwargs):
    options = bf_file_finder_options(**kwargs)
    finder = bf_file_finder(options = options)
    return finder.find(where).sorted_by_criteria('FILENAME')
  
  @classmethod
  def find_with_fnmatch(clazz, where,
                        file_type = bf_file_type.FILE_OR_LINK,
                        path_type = bf_path_type.BASENAME,
                        match_type = bf_file_matcher_type.ALL,
                        min_depth = None,
                        max_depth = None,
                        follow_links = False,
                        include_patterns = None,
                        exclude_patterns = None):
    matcher = None
    if include_patterns or exclude_patterns:
      matcher = bf_file_matcher()
      for pattern in (include_patterns or []):
        matcher.add_item_fnmatch(pattern, path_type = path_type)
      for pattern in (exclude_patterns or []):
        matcher.add_item_fnmatch(pattern, path_type = path_type, negate = True)
    return clazz.find_with_options(where,
                                   file_type = file_type,
                                   match_type = match_type,
                                   min_depth = min_depth,
                                   max_depth = max_depth,
                                   follow_links = follow_links,
                                   file_matcher = matcher)
