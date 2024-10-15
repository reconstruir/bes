#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import os

from collections import namedtuple

from bes.system.check import check
from bes.system.log import logger

from ..bf_entry import bf_entry
from ..bf_entry_list import bf_entry_list
from ..bf_error import bf_error
from ..bf_filename import bf_filename
from ..match.bf_file_matcher import bf_file_matcher
from ..match.bf_file_matcher_type import bf_file_matcher_type

class bf_walk(object):

  _log = logger('bf_walk')

  # based on:
  # https://stackoverflow.com/questions/229186/os-walk-without-digging-into-directories-below
  _bf_walk_item = namedtuple('_bf_walk_item', 'root_dir, dirs, files, depth')
  @classmethod
  def walk(clazz, where, max_depth = None, follow_links = False,
           walk_dir_matcher = None, walk_dir_match_type = None):
    check.check_string(where)
    check.check_int(max_depth, allow_none = True)
    check.check_bool(follow_links)
    check.check_bf_file_matcher(walk_dir_matcher, allow_none = True)
    walk_dir_match_type = check.check_bf_file_matcher_type(walk_dir_match_type, allow_none = True)
    
    where = path.normpath(where.rstrip(path.sep))
    if not path.isdir(where):
      raise bf_error(f'not a directory: {where}')
    num_sep = where.count(path.sep)
    for next_root_dir, dirs, files in os.walk(where, topdown = True, followlinks = follow_links):
      files[:] = sorted(files)
      dirs[:] = sorted(dirs)
      clazz._log.log_d(f'walk_with_depth: next_root_dir={next_root_dir} dirs={dirs} files={files}')
      num_sep_this = next_root_dir.count(path.sep)
      depth = num_sep_this - num_sep
      dir_entries = clazz._make_entry_list(where, next_root_dir, dirs)
      file_entries = clazz._make_entry_list(where, next_root_dir, files)
      walk_item = clazz._bf_walk_item(next_root_dir, dir_entries, file_entries, depth)
      yield walk_item
      if max_depth is not None:
        if num_sep + max_depth - 1 <= num_sep_this:
          del dirs[:]
      else:
        if walk_dir_matcher:
          clazz._log.log_d(f'walk_with_depth: filtering dirs because of walk_dir_matcher')
          filtered_dir_entries = walk_dir_matcher.match_entries(dir_entries,
                                                                match_type = walk_dir_match_type)
          filtered_dirs = filtered_dir_entries.basenames()
          if set(filtered_dirs) != set(dirs):
            clazz._log.log_d(f'walk_with_depth: filtered_dirs={filtered_dirs}')
          else:
            clazz._log.log_d(f'walk_with_depth: filtered_dirs unchanged')
          dirs[:] = filtered_dirs


  @classmethod
  def _make_entry(clazz, where, next_root_dir, filename):
    abs_filename = path.join(next_root_dir, filename)
    rel_filename = bf_filename.remove_head(abs_filename, where)
    #print(f'where={where} next_root_dir={next_root_dir} filename={filename}')
    return bf_entry(rel_filename, root_dir = where)

  @classmethod
  def _make_entry_list(clazz, where, next_root_dir, filenames):
    return bf_entry_list([ clazz._make_entry(where, next_root_dir, f) for f in filenames ])
  
          
