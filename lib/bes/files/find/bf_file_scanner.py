#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import os

from datetime import datetime

from bes.system.check import check
from bes.system.log import logger
from bes.common.object_util import object_util

from ..bf_check import bf_check
from ..bf_entry import bf_entry
from ..bf_file_type import bf_file_type
from ..bf_filename import bf_filename
from ..bf_path_type import bf_path_type
from ..bf_symlink import bf_symlink

from ..ignore.bf_file_ignore import bf_file_ignore

from ..match.bf_file_matcher import bf_file_matcher
from ..match.bf_file_matcher_mode import bf_file_matcher_mode

from ..mime.bf_mime import bf_mime

from .bf_file_scanner_context import bf_file_scanner_context
from .bf_file_scanner_options import bf_file_scanner_options
from .bf_file_scanner_result import bf_file_scanner_result
from .bf_file_scanner_stats import bf_file_scanner_stats
from .bf_walk import bf_walk

class bf_file_scanner(object):

  _log = logger('bf_file_scanner')
  
  def __init__(self, options = None):
    check.check_bf_file_scanner_options(options, allow_none = True)

    self._options = bf_file_scanner_options.clone_or_create(options)
    check.check_bf_file_scanner_options(self._options)

  def scan_gen(self, where):
    where = bf_check.check_dir_seq(object_util.listify(where))
    for next_where in where:
      for entry in self._scan_gen_one_dir(next_where, None):
        yield entry

  def _scan_gen_with_context(self, where, context):
    where = bf_check.check_dir_seq(object_util.listify(where))
    for next_where in where:
      for entry in self._scan_gen_one_dir(next_where, context):
        yield entry
        
  def _scan_gen_one_dir(self, where, context):
    where = bf_check.check_dir(where)
    where = path.normpath(where)
    print(f'entry_list_class={self._options.entry_list_class}', flush = True)
    result = self._options.entry_list_class()
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
                             walk_dir_match_type = self._options.walk_dir_match_type,
                             file_entry_class = self._options.file_entry_class,
                             dir_entry_class = self._options.dir_entry_class):
      self._log.log_d(f'next: {count + 1}: dirs={item.dirs} files={item.files} where={where}')
      if done:
        break
      if context:
        context.stats['depth'] = max(context.stats['depth'], item.depth)
      to_check_files = self._options.entry_list_class()
      to_check_dirs = self._options.entry_list_class()

      if want_files or want_links:
        for next_file_entry in item.files:
          try:
            is_link = next_file_entry.is_link
            if want_links and is_link:
              to_check_files.append(next_file_entry)
            if want_files and not is_link:
              to_check_files.append(next_file_entry)
          except FileNotFoundError as ex:
            print(f'caught {ex} - ignore {next_file_entry.filename}')
            pass

      if want_dirs:
        to_check_dirs += item.dirs

      num_to_check_files = len(to_check_files)
      for i, next_file_entry in enumerate(to_check_files, start = 1):
        p = path.join(where, next_file_entry.relative_filename, '.testing_test_ignore')
        if done:
          self._log.log_d(f'done at file|link {i} of {num_to_check_files}: filename={next_file_entry.relative_filename}')
          break
        if self._entry_matches(next_file_entry, where, context):
          self._log.log_d(f'matched file|link {i} of {num_to_check_files}: filename={next_file_entry.relative_filename}')
          count += 1
          yield next_file_entry
          if self._options.stop_after == count:
            done = True
      matched_dirs = self._options.entry_list_class()
      num_to_check_dirs = len(to_check_dirs)
      for i, next_dir_entry in enumerate(to_check_dirs, start = 1):
        p = path.join(where, next_dir_entry.relative_filename, '.testing_test_ignore')
        if done:
          self._log.log_d(f'done at dir {i} of {num_to_check_dirs}: filename={next_dir_entry.relative_filename}')
          break
        if self._entry_matches(next_dir_entry, where, context):
          self._log.log_d(f'matched dir {i} of {num_to_check_dirs}: filename={next_dir_entry.relative_filename}')
          matched_dirs.append(next_dir_entry)
          count += 1
          yield next_dir_entry
          if self._options.stop_after == count:
            done = True
      self._log.log_d(f'matched_dirs={matched_dirs.basenames()}')

  def _entry_matches(self, entry, where, context):
    where_sep_count = where.count(os.sep)
    depth = entry.absolute_filename.count(os.sep) - where_sep_count
    if context:
      context.stats['num_checked'] += 1
      try:
        if entry.is_dir:
          context.stats['num_dirs_checked'] += 1
      except FileNotFoundError as ex:
        pass
      try:
        if entry.is_file:
          context.stats['num_files_checked'] += 1
      except FileNotFoundError as ex:
        pass
    if not self._options.depth_in_range(depth):
      return False
    if self._options.ignore_broken_links and entry.is_broken_link:
      return False
    if self._should_ignore_entry(entry, where):
      return False
    if not self._options.include_resource_forks and bf_mime.is_apple_resource_fork(entry.filename):
      return False
    return True

  def _should_ignore_entry(self, entry, root_dir):
    if not self._options.ignore_filename:
      return False
    if entry.basename == self._options.ignore_filename:
      return True
    file_ignore = bf_file_ignore(self._options.ignore_filename)
    if file_ignore.should_ignore(entry, root_dir):
      return True
    return False
  
  def scan(self, where):
    context = bf_file_scanner_context()
    entries = self._options.entry_list_class()
    for entry in self._scan_gen_with_context(where, context):
      entries.append(entry)
    return bf_file_scanner_result(entries, context.make_stats())

  @classmethod
  def scan_with_options(clazz, where, **kwargs):
    options = bf_file_scanner_options(**kwargs)
    finder = bf_file_scanner(options = options)
    return finder.scan(where)
