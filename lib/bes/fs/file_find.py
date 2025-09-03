#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import errno, os.path as path, os, stat

from .dir_util import dir_util
from .file_match import file_match
from bes.files.bf_path import bf_path
from .file_util import file_util
from ..common.object_util import object_util

from ..files.find.bf_file_finder import bf_file_finder
from ..files.find.bf_file_finder_options import bf_file_finder_options
from ..files.match.bf_file_matcher import bf_file_matcher
from ..files.match.bf_file_matcher_mode import bf_file_matcher_mode
from ..files.bf_path_type import bf_path_type

class file_find(object):

  FILE = 0x02
  DIR = 0x04
  LINK = 0x08
  DEVICE = 0x10
  ANY = FILE | DIR | LINK | DEVICE
  FILE_OR_LINK = FILE | LINK
  
  @classmethod
  def find(clazz, root_dir, min_depth = None,
           relative = True,
           max_depth = None, file_type = FILE, follow_links = False,
           match_patterns = None, match_type = None, match_basename = True,
           match_function = None, match_re = None):
    result = clazz.find_entries(root_dir,
                                min_depth = min_depth,
                                max_depth = max_depth,
                                file_type = file_type,
                                follow_links = follow_links,
                                match_patterns = match_patterns,
                                match_type = match_type,
                                match_basename = match_basename,
                                match_function = match_function,
                                match_re = match_re)
    if relative:
      filenames = result.entries.relative_filenames(False)
    else:
      filenames = result.entries.absolute_filenames(False)
    return sorted(filenames)

  @classmethod
  def find_entries(clazz, root_dir, min_depth = None,
                   max_depth = None, file_type = FILE, follow_links = False,
                   match_patterns = None, match_type = None, match_basename = True,
                   match_function = None, match_re = None):
    if match_re and not isinstance(match_re, ( list, tuple, set )):
      match_re = object_util.listify(match_re)
    if match_patterns and not isinstance(match_patterns, ( list, tuple, set )):
      match_patterns = object_util.listify(match_patterns)
    matcher = None
    if match_patterns or match_function or match_re:
      matcher = bf_file_matcher()
    if match_basename:
      path_type = bf_path_type.RELATIVE
    else:
      path_type = bf_path_type.ABSOLUTE
    if match_patterns:
      for pattern in match_patterns:
        matcher.add_item_fnmatch(pattern, path_type = path_type)
    if match_re:
      for expression in match_re:
        matcher.add_item_re(expression, path_type = path_type)
    if match_function:
      matcher.add_item_callable(match_function, path_type = path_type)
    assert isinstance(match_basename, bool)

    match_type_map = {
      file_match.ALL: bf_file_matcher_mode.ALL,
      file_match.NONE: bf_file_matcher_mode.NONE,
      file_match.ANY: bf_file_matcher_mode.ANY,
    }
    if match_type:
      match_type = match_type_map[match_type]
    else:
      match_type = bf_file_matcher_mode.ANY
    return bf_file_finder.find_with_options(root_dir,
                                            min_depth = min_depth,
                                            max_depth = max_depth,
                                            file_type = file_type,
                                            follow_links = follow_links,
                                            file_matcher = matcher,
                                            match_type = match_type)
  
  @classmethod
  def find_function(clazz, root_dir, function,
                    relative = True,
                    min_depth = None, max_depth = None,
                    file_type = FILE, follow_links = False, match_basename = True):
    assert callable(function)
    return clazz.find(root_dir, min_depth = min_depth, relative = relative,
                      max_depth = max_depth, file_type = file_type, follow_links = follow_links,
                      match_function = function, match_basename = match_basename)

  @classmethod
  def find_fnmatch(clazz, root_dir, patterns, match_type = file_match.ANY,
                   relative = True,
                   min_depth = None, max_depth = None,
                   file_type = FILE, follow_links = False, match_basename = True):
    assert patterns
    assert match_type
    return clazz.find(root_dir, min_depth = min_depth, relative = relative,
                      max_depth = max_depth, file_type = file_type, follow_links = follow_links,
                      match_patterns = patterns, match_type = match_type, match_basename = match_basename)

  @classmethod
  def find_re(clazz, root_dir, expressions, match_type = file_match.ANY,
              relative = True,
              min_depth = None, max_depth = None,
              file_type = FILE, follow_links = False, match_basename = True):
    assert expressions
    assert match_type
    return clazz.find(root_dir, min_depth = min_depth, relative = relative,
                      max_depth = max_depth, file_type = file_type, follow_links = follow_links,
                      match_re = expressions, match_type = match_type, match_basename = match_basename)

  @classmethod
  def find_dirs(clazz, root_dir, min_depth = None, max_depth = None,
                follow_links = False, match_basename = True):
    return clazz.find(root_dir, min_depth = min_depth,  max_depth = max_depth,
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
      start_dir = bf_path.parent_dir(start_dir)
      if path.ismount(start_dir):
        return None

  @classmethod
  def find_unreadable(clazz, d, relative = True):
    'Return files and dirs that are unreadable.'
    result = clazz.find_entries(d, file_type = file_find.ANY)
    entries = result.entries
    unreadable = entries.unreadable_files()
    if relative:
      return entries.relative_filenames(False)
    else:
      return entries.absolute_filenames(False)

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
