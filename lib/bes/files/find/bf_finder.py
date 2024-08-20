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

from .bf_finder_options import bf_finder_options

class bf_finder(object):

  def __init__(self, options = None):
    check.check_bf_finder_options(options, allow_none = True)

    self._options = options or bf_finder_options()

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
  def find_with_options(clazz, where, **kwargs):
    options = bf_finder_options(**kwargs)
    finder = bf_finder(options = options)
    return finder.find(where).sorted_caca('FILENAME')
  
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
