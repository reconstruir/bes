#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import re

from bes.common.algorithm import algorithm
from bes.fs.file_check import file_check
from bes.fs.file_mime import file_mime
from bes.fs.file_path import file_path
from bes.fs.file_find import file_find
from bes.fs.file_match import file_match
from bes.fs.file_resolver import file_resolver
from bes.fs.file_resolver_options import file_resolver_options
from bes.fs.file_search import file_search
from bes.fs.file_util import file_util
from bes.fs.filename_util import filename_util
from bes.system.python import python
from bes.system.check import check

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
    return resolved.files()

  @classmethod
  def resolve_text_files(clazz, files):
    'Resolve text files.'
    
    def _match_function(filename):
      return file_mime.is_text(filename)
    options = file_resolver_options(match_function = _match_function,
                                    match_basename = False)
    resolved = file_resolver.resolve_files(files, options = options)
    return resolved.files()
  
  @classmethod
  def search_files(clazz, files, text, word_boundary = False, ignore_case = False):
    'Search for text in files.'
    
    result = []
    for filename in files:
      next_matches = file_search.search_file(filename, text,
                                             word_boundary = word_boundary,
                                             ignore_case = ignore_case)
      result.extend(next_matches)
    return sorted(algorithm.unique([ item.filename for item in result ]))

  @classmethod
  def rename_dirs(clazz, src_pattern, dst_pattern, root_dir, word_boundary = False):
    check.check_string(src_pattern)
    check.check_string(dst_pattern)
    check.check_string(root_dir)
    check.check_bool(word_boundary)

    if src_pattern in dst_pattern:
      raise refactor_error(f'src_pattern "{src_pattern}" cannot be a substring in dst_pattern "{dst_pattern}"')
    if dst_pattern in src_pattern:
      raise refactor_error(f'dst_pattern "{dst_pattern}" cannot be a substring in src_pattern "{src_pattern}"')

    escaped_src_pattern = re.escape(src_pattern)
    if word_boundary:
      expression = r'.*\b{}\b.*'.format(escaped_src_pattern)
    else:
      expression = r'.*{}.*'.format(escaped_src_pattern)

    def _match_function(d):
      assert path.isdir(d)
      return file_match.match_re(d, expression, match_type = file_match.ANY, basename = True)
    options = file_resolver_options(match_function = _match_function,
                                    match_basename = False,
                                    sort_order = 'depth',
                                    sort_reverse = True)

    while True:
      resolved = file_resolver.resolve_dirs(root_dir, options = options)
      if not resolved:
        break;
      
      rel_dirs = [ d.filename for d in resolved ]
      for next_dir in rel_dirs:
        replaced_dir = file_path.replace(next_dir,
                                         src_pattern,
                                         dst_pattern,
                                         count = 1,
                                         backwards = True)
        assert replaced_dir != next_dir
        src_dir_abs = path.join(root_dir, next_dir)
        dst_dir_abs = path.join(root_dir, replaced_dir)
        file_util.rename(src_dir_abs, dst_dir_abs)

  @classmethod
  def _minimum_path(clazz, p, src_pattern):
    v = file_path.split(p)
    result = []
    for x in v:
      result.append(x)
      if src_pattern in x:
        break
    return file_path.join(result)

  @classmethod
  def _minimum_paths(clazz, paths, src_pattern):
    return algorithm.unique([ clazz._minimum_path(p, src_pattern) for p in paths ])
  
