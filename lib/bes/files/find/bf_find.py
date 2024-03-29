#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import os

#import errno, os.path as path, os, stat
#
#from .dir_util import dir_util
#from .file_path import file_path

from bes.system.check import check

from ..bf_check import bf_check
from ..bf_entry import bf_entry
from ..bf_entry_list import bf_entry_list
from ..bf_filename import bf_filename
from ..bf_file_type import bf_file_type

from .bf_find_options import bf_find_options

class bf_find(object):

  def __init__(self, options = None):
    check.check_bf_find_options(options, allow_none = True)

    self._options = options or bf_find_options()

  def find_gen(self, where):
    where = bf_check.check_dir(where)
    where = path.normpath(where)
    result = bf_entry_list()
    where = path.normpath(where)
    where_sep_count = where.count(os.sep)
    
    for root, dirs, files in self.walk_with_depth(where,
                                                  max_depth = self._options.max_depth,
                                                  follow_links = self._options.follow_links):
      to_check = []
      if self._options.file_type.mask_matches(bf_file_type.ANY_FILE):
        to_check += files
      if self._options.file_type.mask_matches(bf_file_type.DIR):
        to_check += dirs
      else:
        links = [ d for d in dirs if path.islink(path.normpath(path.join(root, d))) ]
        to_check += links
      for name in to_check:
        abs_filename = path.normpath(path.join(root, name))
        entry = bf_entry(abs_filename, root_dir = where)
        depth = abs_filename.count(os.sep) - where_sep_count
        if self._entry_matches(entry, depth, self._options):
          if self._options.relative:
            relative_filename = bf_filename.remove_head(abs_filename, where)
            entry = bf_entry(relative_filename, root_dir = root)
          yield entry

  def find(self, where):
    result = bf_entry_list()
    for entry in self.find_gen(where):
      result.append(entry)
    return result
          
  @classmethod
  def _entry_matches(clazz, entry, depth, options):
    if not options.depth_in_range(depth):
      return False
    if not entry.file_type_matches(options.file_type):
      return False
    if not options.file_match_matches(entry):
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
  def find_dirs(clazz, root_dir, relative = True, min_depth = None, max_depth = None,
                follow_links = False, match_basename = True):
    return clazz.find(root_dir, relative = relative, min_depth = min_depth,  max_depth = max_depth,
                      file_type = clazz.DIR, follow_links = follow_links, match_basename = match_basename)

  @classmethod
  def find_in_ancestors(clazz, start_dir, filename):
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
