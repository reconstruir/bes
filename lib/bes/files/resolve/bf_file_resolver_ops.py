#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import os

from bes.system.check import check

from ..bf_check import bf_check
from ..bf_entry import bf_entry
from ..bf_entry_list import bf_entry_list
from ..bf_file_type import bf_file_type
from ..bf_filename import bf_filename
from ..bf_path import bf_path

from .bf_file_resolver_options import bf_file_resolver_options
from .bf_file_resolver import bf_file_resolver

class bf_file_resolver_ops(object):
  
  @classmethod
  def resolve_dirs(clazz, root_dir, relative = True, min_depth = None, max_depth = None,
                   follow_links = False, path_type = 'basename'):
    root_dir = bf_check.check_dir(root_dir)
    
    options = bf_file_resolver_options(file_type = bf_file_type.DIR,
                                       relative = relative,
                                       min_depth = min_depth,
                                       max_depth = max_depth,
                                       follow_links = follow_links,
                                       path_type = path_type)
    resolver = bf_file_resolver(options)
    return resolver.resolve(where)
  
  @classmethod
  def resolve_in_ancestors(clazz, start_dir, filename):
    root_dir = bf_check.check_dir(start_dir)
    check.check_string(filename)
    
    if path.isfile(start_dir):
      start_dir = path.dirname(start_dir)
    assert path.isdir(start_dir)
    while True:
      what = path.join(start_dir, filename)
      if path.exists(what):
        return what
      start_dir = bf_path.parent_dir(start_dir)
      if path.ismount(start_dir):
        return None

  @classmethod
  def resolve_unreadable(clazz, d, relative = True):
    'Return files and dirs that are unreadable.'
    files = clazz.resolve(d, relative = relative, file_type = file_resolve.ANY)
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
  def resolve_empty_dirs(clazz, root_dir, relative = True, min_depth = None, max_depth = None):
    
    return clazz.resolve(root_dir,
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
      empties = clazz.resolve_empty_dirs(root_dir, relative = False, min_depth = min_depth, max_depth = max_depth)
      if not empties:
        break
      for next_empty in empties:
        dir_util.remove(next_empty)
        result.append(next_empty)
    if dir_util.is_empty(root_dir):
      dir_util.remove(root_dir)
      result.append(root_dir)
    return sorted(result)
