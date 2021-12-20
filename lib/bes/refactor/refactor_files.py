#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.algorithm import algorithm
from bes.fs.file_check import file_check
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
from bes.system.check import check
from bes.system.python import python
from bes.git.git import git

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
  
  @classmethod
  def search_files(clazz, files, text, word_boundary = False):
    'Search for text in files.'
    
    result = []
    for filename in files:
      next_matches = file_search.search_file(filename, text,
                                             word_boundary = word_boundary)
      result.extend(next_matches)
    return sorted(algorithm.unique([ item.filename for item in result ]))

  @classmethod
  def rename_dirs(clazz, src_pattern, dst_pattern, root_dir,
                  word_boundary = False):
    check.check_string(src_pattern)
    check.check_string(dst_pattern)
    check.check_string(root_dir)
    check.check_bool(word_boundary)

    if src_pattern in dst_pattern:
      raise refactor_error(f'src_pattern "{src_pattern}" cannot be a substring in dst_pattern "{dst_pattern}"')
    if dst_pattern in src_pattern:
      raise refactor_error(f'dst_pattern "{dst_pattern}" cannot be a substring in src_pattern "{src_pattern}"')

    options = clazz._make_file_resolver_options(src_pattern, word_boundary)
    while True:
      resolved_dirs = file_resolver.resolve_dirs(root_dir, options = options)
      if not resolved_dirs:
        break;
      clazz._rename_many(resolved_dirs.relative_files(), root_dir, src_pattern, dst_pattern, False)

  @classmethod
  def _rename_one(clazz, src, dst, try_git):
    renamed = False
    if try_git:
      try:
        git.move(os.getcwd(), src, dst)
        renamed = True
      except Exception as ex:
        pass
    if not renamed:
      file_util.rename(src, dst)
        
  @classmethod
  def _rename_many(clazz, files, root_dir, src_pattern, dst_pattern, try_git):
    for next_filename in files:
      replaced_filename = file_path.replace(next_filename,
                                            src_pattern,
                                            dst_pattern,
                                            count = 1,
                                            backwards = True)
      assert replaced_filename != next_filename
      src_filename_abs = path.join(root_dir, next_filename)
      dst_filename_abs = path.join(root_dir, replaced_filename)
      clazz._rename_one(src_filename_abs, dst_filename_abs, try_git)
        
  @classmethod
  def rename_files(clazz, src_pattern, dst_pattern, root_dir,
                   word_boundary = False):
    check.check_string(src_pattern)
    check.check_string(dst_pattern)
    check.check_string(root_dir)
    check.check_bool(word_boundary)

    if src_pattern in dst_pattern:
      raise refactor_error(f'src_pattern "{src_pattern}" cannot be a substring in dst_pattern "{dst_pattern}"')
    if dst_pattern in src_pattern:
      raise refactor_error(f'dst_pattern "{dst_pattern}" cannot be a substring in src_pattern "{src_pattern}"')

    options = clazz._make_file_resolver_options(src_pattern, word_boundary)
    resolved_files = file_resolver.resolve_files(root_dir, options = options)
    clazz._rename_many(resolved_files.relative_files(), root_dir, src_pattern, dst_pattern, False)
      
  @classmethod
  def _make_file_resolver_options(clazz, src_pattern, word_boundary):
    def _match_function(d):
      return clazz._match_basename(path.basename(d), src_pattern, word_boundary)
    return file_resolver_options(match_function = _match_function,
                                 match_basename = False,
                                 sort_order = 'depth',
                                 sort_reverse = True)

  @classmethod
  def _match_basename(clazz, basename, pattern, word_boundary):
    i = basename.find(pattern)
    if i < 0:
      return False
    if not word_boundary:
      return True
    if i > 0:
      left_index = i - 1
    else:
      left_index = None
    right_index = i + len(pattern)
    if right_index == len(basename):
      right_index = None
    if left_index != None:
      if basename[left_index].isalnum():
        return False
    if right_index != None:
      if basename[right_index].isalnum():
        return False
    return True
