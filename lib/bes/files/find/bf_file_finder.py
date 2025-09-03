#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime

from bes.system.check import check
from bes.system.log import logger

from ..bf_check import bf_check
from ..bf_entry import bf_entry
from ..bf_entry_list import bf_entry_list
from ..bf_file_type import bf_file_type
from ..bf_path_type import bf_path_type
from ..match.bf_file_matcher_mode import bf_file_matcher_mode
from ..match.bf_file_matcher import bf_file_matcher

from .bf_file_finder_options import bf_file_finder_options
from .bf_file_finder_result import bf_file_finder_result
from .bf_file_finder_stats import bf_file_finder_stats

from .bf_file_scanner import bf_file_scanner

class bf_file_finder(object):

  _log = logger('bf_file_finder')
  
  def __init__(self, options = None):
    check.check_bf_file_finder_options(options, allow_none = True)

    self._options = bf_file_finder_options.clone_or_create(options)
    check.check_bf_file_finder_options(self._options)

  def find_gen(self, where):
    scanner = bf_file_scanner(options = self._options)

    for next_entry in scanner.scan_gen(where):
      if self._options.found_callback:
        self._options.found_callback(next_entry)
      if not self._options.file_matcher_matches(next_entry):
        continue
      yield next_entry

  def _find_gen_with_stats(self, where, stats_dict):
    scanner = bf_file_scanner(options = self._options)

    for next_entry in scanner._scan_gen_with_stats(where, stats_dict):
      if self._options.found_callback:
        self._options.found_callback(next_entry)
      if not self._options.file_matcher_matches(next_entry):
        continue
      yield next_entry
        
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
                        match_type = bf_file_matcher_mode.ALL,
                        min_depth = None,
                        max_depth = None,
                        follow_links = False,
                        include_patterns = None,
                        exclude_patterns = None,
                        walk_dir_matcher = None,
                        walk_dir_match_type = None):
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
                                   file_matcher = matcher,
                                   walk_dir_matcher = walk_dir_matcher,
                                   walk_dir_match_type = walk_dir_match_type)
