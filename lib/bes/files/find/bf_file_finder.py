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
    where_sep_count = where.count(os.sep)

    self._log.log_d(f'find_gen: where={where} options={self._options}')

    count = 0
    done = False
    for item in bf_walk.walk(where,
                             max_depth = self._options.max_depth,
                             follow_links = self._options.follow_links):
      root = item.root_dir
      dirs = item.dirs.basenames()
      files = item.files.basenames()
      depth = item.depth
      if done:
        break
      if stats_dict:
        stats_dict['depth'] = max(stats_dict['depth'], depth)
      to_check_files = []
      to_check_dirs = []
      to_check_links = []

      want_files = self._options.file_type.mask_matches(bf_file_type.FILE)
      want_dirs = self._options.file_type.mask_matches(bf_file_type.DIR)
      want_links = self._options.file_type.mask_matches(bf_file_type.LINK)

      if want_files or want_links:
        for next_file in files:
          next_file_path = path.normpath(path.join(root, next_file))
          is_link = path.islink(next_file_path)
          if want_links and is_link:
            to_check_links.append(next_file)
          if want_files and not is_link:
            to_check_files.append(next_file)

      if want_dirs:
        to_check_dirs += dirs
        
      to_check_files_and_links = to_check_files + to_check_links
      for i, name in enumerate(to_check_files_and_links, start = 1):
        self._log.log_d(f'checking file|link {i} of {len(to_check_files_and_links)}: root={root} name={name} done={done}')
        if done:
          break
        matched_entry = self._check_one(root, name, where, where_sep_count, stats_dict)
        if matched_entry:
          count += 1
          if self._options.found_callback:
            self._options.found_callback(matched_entry)
          yield matched_entry
          if self._options.stop_after == count:
            done = True
      matched_dirs = []
      for i, name in enumerate(to_check_dirs, start = 1):
        self._log.log_d(f'checking dirs {i} of {len(to_check_dirs)}: {name} done={done}')
        if done:
          break
        matched_entry = self._check_one(root, name, where, where_sep_count, stats_dict)
        if matched_entry:
          matched_dirs.append(name)
          count += 1
          if self._options.found_callback:
            self._options.found_callback(matched_entry)
          yield matched_entry
          if self._options.stop_after == count:
            done = True
      self._log.log_d(f'matched_dirs={matched_dirs}')
      #dirs[:] = matched_dirs

  def _check_one(self, root, name, where, where_sep_count, stats_dict):
    #print(f'_check_one: root={root} name={name} where={where} where_sep_count={where_sep_count}')
    
    abs_filename = path.normpath(path.join(root, name))
    rel_filename = bf_filename.remove_head(abs_filename, where)
    entry = bf_entry(rel_filename, root_dir = where)
    depth = abs_filename.count(os.sep) - where_sep_count
    if stats_dict:
      stats_dict['num_checked'] += 1
      if entry.is_dir:
        stats_dict['num_dirs_checked'] += 1
      if entry.is_file:
        stats_dict['num_files_checked'] += 1
    if self._entry_matches(entry, depth, self._options):
      if self._options.relative:
        relative_filename = bf_filename.remove_head(abs_filename, where)
        entry = bf_entry(relative_filename, root_dir = root)
      return entry
    return None
    
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
  def _entry_matches(clazz, entry, depth, options):
    if not options.depth_in_range(depth):
      return False
    if options.ignore_broken_links and bf_symlink.is_broken(entry.filename):
      return False
    if not entry.file_type_matches(options.file_type):
      return False
    if not options.file_matcher_matches(entry):
      return False
    return True
              
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
                        relative = True,
                        min_depth = None,
                        max_depth = None,
                        follow_links = False,
                        include_patterns = None,
                        exclude_patterns = None):
    matcher = None
    if include_patterns or exclude_patterns:
      matcher = bf_file_matcher()
      for pattern in (include_patterns or []):
        matcher.add_matcher_fnmatch(pattern)
      for pattern in (exclude_patterns or []):
        matcher.add_matcher_fnmatch(pattern, negate = True)
    return clazz.find_with_options(where,
                                   file_type = file_type,
                                   path_type = path_type,
                                   match_type = match_type,
                                   relative = relative,
                                   min_depth = min_depth,
                                   max_depth = max_depth,
                                   follow_links = follow_links,
                                   file_matcher = matcher)
