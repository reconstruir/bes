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

class bf_file_finder(object):

  _log = logger('bf_file_finder')
  
  def __init__(self, options = None):
    check.check_bf_file_finder_options(options, allow_none = True)

    self._options = options or bf_file_finder_options()

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
    for root, dirs, files in self.walk_with_depth(where,
                                                  max_depth = self._options.max_depth,
                                                  follow_links = self._options.follow_links):
      #print(f'checking root={root} dirs={dirs}', flush = True)
      if done:
        break
      to_check = []
      if self._options.file_type.mask_matches(bf_file_type.ANY_FILE):
        to_check += files
      if self._options.file_type.mask_matches(bf_file_type.DIR):
        to_check += dirs
      else:
        links = [ d for d in dirs if path.islink(path.normpath(path.join(root, d))) ]
        to_check += links
      for name in to_check:
        if done:
          break
        abs_filename = path.normpath(path.join(root, name))
        entry = bf_entry(abs_filename, root_dir = where)
        depth = abs_filename.count(os.sep) - where_sep_count
        if stats_dict:
          stats_dict['num_checked'] += 1
        if self._entry_matches(entry, depth, self._options):
          if self._options.relative:
            relative_filename = bf_filename.remove_head(abs_filename, where)
            entry = bf_entry(relative_filename, root_dir = root)
          count += 1
          if self._options.found_callback:
            self._options.found_callback(entry)
          yield entry
          if self._options.stop_after == count:
            done = True
            
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
              
  #: https://stackoverflow.com/questions/229186/os-walk-without-digging-into-directories-below
  @classmethod
  def walk_with_depth(clazz, root_dir, max_depth = None, follow_links = False):
    root_dir = root_dir.rstrip(path.sep)
    if not path.isdir(root_dir):
      raise RuntimeError('not a directory: %s' % (root_dir))
    num_sep = root_dir.count(path.sep)
    for root, dirs, files in os.walk(root_dir, topdown = True, followlinks = follow_links):
      #print(" root: %s" % (root))
      #print(" dirs: %s" % (' '.join(dirs)))
      #print("files: %s" % (' '.join(files)))
      #print("")
      yield root, dirs, files
      num_sep_this = root.count(path.sep)
      if max_depth is not None:
        if num_sep + max_depth - 1 <= num_sep_this:
          del dirs[:]

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
