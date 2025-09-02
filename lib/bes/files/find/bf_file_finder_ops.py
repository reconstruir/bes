#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import os

from bes.system.check import check
from bes.common.object_util import object_util

from ..bf_check import bf_check
from ..bf_entry import bf_entry
from ..bf_entry_list import bf_entry_list
from ..bf_filename import bf_filename
from ..bf_file_type import bf_file_type
from ..bf_path_type import bf_path_type

from .bf_file_finder_options import bf_file_finder_options
from .bf_file_finder import bf_file_finder

class bf_file_finder_ops(object):

  @classmethod
  def find(clazz, where, file_type, min_depth = None, max_depth = None, follow_links = False):
    where = bf_check.check_dir_seq(object_util.listify(where))
    file_type = check.check_bf_file_type(file_type)

    options = bf_file_finder_options(file_type = file_type,
                                     min_depth = min_depth,
                                     max_depth = max_depth,
                                     follow_links = follow_links)
    finder = bf_file_finder(options)
    return finder.find(where)
  
  @classmethod
  def find_dirs(clazz, where, min_depth = None, max_depth = None, follow_links = False):
    return clazz.find(where,
                      bf_file_type.DIR,
                      min_depth = min_depth,
                      max_depth = max_depth,
                      follow_links = follow_links)

  @classmethod
  def find_files(clazz, where, min_depth = None, max_depth = None, follow_links = False):
    return clazz.find(where,
                      bf_file_type.FILE,
                      min_depth = min_depth,
                      max_depth = max_depth,
                      follow_links = follow_links)
  
  @classmethod
  def find_in_ancestors(clazz, start_dir, filename):
    root_dir = bf_check.check_dir(start_dir)
    check.check_string(filename)
    
    if path.isfile(start_dir):
      start_dir = path.dirname(start_dir)
    assert path.isdir(start_dir)
    while True:
      what = path.join(start_dir, filename)
      if path.exists(what):
        return what
      start_dir = file_path.parent_dir(start_dir)
      if path.ismount(start_dir):
        return None

  @classmethod
  def find_unreadable(clazz, d, relative = True):
    'Return files and dirs that are unreadable.'
    files = clazz.find(d, relative = relative, file_type = file_find.ANY)
    result = []
    for filename in files:
      if relative:
        filename_abs = path.join(d, filename)
      else:
        filename_abs = filename
      if not os.access(filename_abs, os.R_OK):
        result.append(filename)
    return result

  @classmethod
  def find_empty_dirs(clazz, root_dir, relative = True, min_depth = None, max_depth = None):
    
    return clazz.find(root_dir,
                      relative = relative,
                      file_type = clazz.DIR,
                      min_depth = min_depth,
                      max_depth = max_depth,
                      match_function = lambda f: dir_util.is_empty(f),
                      match_basename = False)

  @classmethod
  def remove_empty_dirs(clazz, root_dir, min_depth = None, max_depth = None):
    result = []
    while True:
      empties = clazz.find_empty_dirs(root_dir, relative = False, min_depth = min_depth, max_depth = max_depth)
      if not empties:
        break
      for next_empty in empties:
        dir_util.remove(next_empty)
        result.append(next_empty)
    if dir_util.is_empty(root_dir):
      dir_util.remove(root_dir)
      result.append(root_dir)
    return sorted(result)
