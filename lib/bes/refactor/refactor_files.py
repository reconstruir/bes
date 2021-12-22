#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import os
from os import path

from bes.common.algorithm import algorithm
from bes.fs.dir_util import dir_util
from bes.fs.file_check import file_check
from bes.fs.file_find import file_find
from bes.fs.file_find import file_find
from bes.fs.file_match import file_match
from bes.fs.file_mime import file_mime
from bes.fs.file_path import file_path
from bes.fs.file_replace import file_replace
from bes.fs.file_resolver import file_resolver
from bes.fs.file_resolver_options import file_resolver_options
from bes.fs.file_search import file_search
from bes.fs.file_util import file_util
from bes.fs.filename_util import filename_util
from bes.git.git import git
from bes.git.git_error import git_error
from bes.system.check import check
from bes.system.log import logger
from bes.system.python import python

from .refactor_error import refactor_error

class refactor_files(object):
  
  @classmethod
  def resolve_python_files(clazz, files):
    'Resolve python files.'
    
    def _match_function(filename):
      if not file_mime.is_text(filename):
        return False
      if python.is_python_script(filename):
        return True
      return filename_util.has_extension(filename.lower(), 'py')
    options = file_resolver_options(match_function = _match_function,
                                    match_basename = False)
    resolved = file_resolver.resolve_files(files, options = options)
    return resolved.absolute_files(sort = True)

  @classmethod
  def resolve_text_files(clazz, files):
    'Resolve text files.'
    
    def _match_function(filename):
      return file_mime.is_text(filename)
    options = file_resolver_options(match_function = _match_function,
                                    match_basename = False)
    resolved = file_resolver.resolve_files(files, options = options)
    return resolved.absolute_files(sort = True)

  _rename_item = namedtuple('_rename_item', 'src_filename, dst_filename')
  _affected_dir = namedtuple('_affected_dir', 'root_dir, dirname')
  _log = logger('refactor')
  @classmethod
  def rename_files(clazz, files, src_pattern, dst_pattern, word_boundary = False, try_git = False):
    check.check_string(src_pattern)
    check.check_string(dst_pattern)
    check.check_bool(word_boundary)

    clazz._log.log_method_d()

    options = file_resolver_options(sort_order = 'depth',
                                    sort_reverse = True)
    resolved_files = file_resolver.resolve_files(files, options = options)
    rename_items, affected_dirs = clazz._make_rename_items(resolved_files, src_pattern, dst_pattern)
    new_dirs = algorithm.unique([ path.dirname(item.dst_filename) for item in rename_items ])
    new_dirs = [ d for d in new_dirs if d and not path.exists(d) ]
    for next_new_dir in new_dirs:
      file_util.mkdir(next_new_dir)
    for next_rename_item in rename_items:
      clazz._rename_one(next_rename_item.src_filename,
                        next_rename_item.dst_filename,
                        try_git)
    for d in affected_dirs:
      if dir_util.is_empty(d):
        dir_util.remove(d)

  @classmethod
  def _make_rename_items(clazz, resolved_files, src_pattern, dst_pattern):
    rename_items = []
    affected_dirs = []
    for f in resolved_files:
      src_filename_rel = f.filename
      dst_filename_rel = file_path.replace_all(src_filename_rel, src_pattern, dst_pattern)
      if src_filename_rel != dst_filename_rel:
        affected_dirs.append(clazz._affected_dir(f.root_dir, path.dirname(f.filename)))
        src_filename_abs = path.join(f.root_dir, src_filename_rel)
        dst_filename_abs = path.join(f.root_dir, dst_filename_rel)
        item = clazz._rename_item(src_filename_abs, dst_filename_abs)
        rename_items.append(item)
    affected_dirs = sorted(algorithm.unique(affected_dirs))
    decomposed_affected_items = []
    for f in affected_dirs:
      next_paths = file_path.decompose(path.sep + f.dirname)
      for next_path in next_paths:
        item = clazz._affected_dir(f.root_dir, file_util.lstrip_sep(next_path))
        decomposed_affected_items.append(item)
    decomposed_affected_items = sorted(decomposed_affected_items, key = lambda item: file_path.depth(item.dirname), reverse = True)
    decomposed_affected_dirs = [ path.join(item.root_dir, item.dirname) for item in decomposed_affected_items ]
    return rename_items, decomposed_affected_dirs

  @classmethod
  def _rename_one(clazz, src, dst, try_git):
    renamed = False
    if try_git:
      try:
        git.move(os.getcwd(), src, dst)
        renamed = True
      except git_error as ex:
        print(f'caught: {ex}')
    if not renamed:
      file_util.rename(src, dst)
  
  @classmethod
  def search_files(clazz, filenames, text, word_boundary = False, ignore_case = False):
    'Return only the text files in filesnames.'
    result = []
    for filename in filenames:
      result += file_search.search_file(filename, text, word_boundary = word_boundary, ignore_case = ignore_case)
    return result

  @classmethod
  def match_files(clazz, filenames, text, word_boundary = False, ignore_case = False):
    search_rv = clazz.search_files(filenames, text, word_boundary = word_boundary)
    return sorted(algorithm.unique([ s.filename for s in search_rv ]))
