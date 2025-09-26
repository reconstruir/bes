#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime

from bes.system.check import check
from bes.system.log import logger

from ..bf_check import bf_check
from ..bf_entry import bf_entry
from ..bf_file_type import bf_file_type
from ..bf_path_type import bf_path_type
from ..match.bf_file_matcher_mode import bf_file_matcher_mode
from ..match.bf_file_matcher import bf_file_matcher

from .bf_file_finder_mode import bf_file_finder_mode
from .bf_file_finder_options import bf_file_finder_options
from .bf_file_finder_progress_state import bf_file_finder_progress_state
from .bf_file_scanner import bf_file_scanner
from .bf_file_scanner_context import bf_file_scanner_context
from .bf_file_scanner_result import bf_file_scanner_result
from .bf_file_scanner_stats import bf_file_scanner_stats

class bf_file_finder(object):

  _log = logger('bf_file_finder')
  
  def __init__(self, options = None):
    check.check_bf_file_finder_options(options, allow_none = True)

    self._options = bf_file_finder_options.clone_or_create(options)
    check.check_bf_file_finder_options(self._options)

  def find_gen(self, where):
    return self._find_gen(where, None)

  def _find_gen(self, where, context):
    if self._options.mode == bf_file_finder_mode.IMMEDIATE:
      return self._find_gen_mode_immediate(where, context)
    elif self._options.mode == bf_file_finder_mode.WITH_PROGRESS:
      return self._find_gen_mode_with_progress(where, context)
    
  def _find_gen_mode_immediate(self, where, context):
    scanner = bf_file_scanner(options = self._options)

    for next_entry in scanner._scan_gen_with_context(where, context):
      if not self._options.file_matcher_matches(next_entry):
        continue
      yield next_entry

  def _find_gen_mode_with_progress(self, where, context):
    scanner = bf_file_scanner(options = self._options)

    self._options.call_progress_callback(bf_file_finder_progress_state.SCANNING)
    entries = []
    for next_entry in scanner._scan_gen_with_context(where, context):
      entries.append(next_entry)
        
    for index, next_entry in enumerate(entries, start = 1):
      self._options.call_progress_callback(bf_file_finder_progress_state.FINDING,
                                           next_entry,
                                           index,
                                           len(entries))
      if not self._options.file_matcher_matches(next_entry):
        continue
      yield next_entry

    self._options.call_progress_callback(bf_file_finder_progress_state.FINISHED)
      
  def find(self, where):
    context = bf_file_scanner_context()
    entries = self._options.entry_list_class()
    for entry in self._find_gen(where, context):
      entries.append(entry)
    return bf_file_scanner_result(entries, context.make_stats())

  @classmethod
  def find_with_options(clazz, where, **kwargs):
    options = bf_file_finder_options(**kwargs)
    finder = bf_file_finder(options = options)
    return finder.find(where)
  
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
