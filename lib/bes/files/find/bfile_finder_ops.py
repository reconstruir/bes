#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import os

#import errno, os.path as path, os, stat
#
#from .dir_util import dir_util
#from .file_match import file_match
#from .file_path import file_path
#from .file_util import file_util
#from .temp_file import temp_file

from bes.system.check import check

from ..bfile_check import bfile_check
from ..bfile_entry import bfile_entry
from ..bfile_entry_list import bfile_entry_list
from ..bfile_filename import bfile_filename
from ..bfile_type import bfile_type

from .bfile_finder_options import bfile_finder_options
from .bfile_finder import bfile_finder

class bfile_finder_ops(object):

  @classmethod
  def find_dirs(clazz, root_dir, relative = True, min_depth = None, max_depth = None,
                follow_links = False, path_type = 'basename'):
    root_dir = bfile_check.check_dir(root_dir)
    
    options = bfile_finder_options(file_type = bfile_type.DIR,
                                   relative = relative,
                                   min_depth = min_depth,
                                   max_depth = max_depth,
                                   follow_links = follow_links,
                                   path_type = path_type)
    finder = bfile_finder(options)
    return finder.find(where)

  @classmethod
  def find_in_ancestors(clazz, start_dir, filename):
    root_dir = bfile_check.check_dir(start_dir)
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
