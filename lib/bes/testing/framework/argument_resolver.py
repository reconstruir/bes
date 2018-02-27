#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import fnmatch, os.path as path
from bes.common import algorithm
from bes.fs import file_ignore, file_path, file_util
from bes.git import git

from .config_env import config_env
from .file_filter import file_filter
from .file_finder import file_finder
from .file_info import file_info
from .file_info_list import file_info_list
from .unit_test_description import unit_test_description
from .unit_test_inspect import unit_test_inspect

class argument_resolver(object):

  def __init__(self, working_dir, arguments, ignore_patterns, file_ignore_filename = None):
    self.working_dir = path.abspath(working_dir)
    self.arguments = arguments
    self.ignore_patterns = ignore_patterns
    self.file_ignore = file_ignore(file_ignore_filename)
    self.files, self.filters = self._separate_files_and_filters(self.working_dir, self.arguments)
    self.filter_patterns = self._make_filters_patterns(self.filters)
    files = self._resolve_files_and_dirs(self.working_dir, self.files)
    self.root_of_roots = self._find_root_of_roots(files)
    self.config_env = config_env(self.root_of_roots)
    files = self.file_ignore.filter_files(files)
    file_infos = file_info_list([ file_info(self.config_env, f) for f in files ])
    file_infos += self._tests_for_many_files(file_infos)
    file_infos.remove_dups()
    self.inspect_map = file_infos.make_inspect_map()
    # FIXME: change to ignore_without_tests()
    file_infos = file_info_list([ f for f in file_infos if f.filename in self.inspect_map ])
    # FIXME: change to filter_with_patterns_tests()
    file_infos = file_infos.filter_by_filenames(self.filter_patterns)
    self.files_and_tests = file_filter.poto_filter_files(file_infos, self.filter_patterns)
    if self.ignore_patterns:
      self.files_and_tests = file_filter.ignore_files(self.files_and_tests, self.ignore_patterns)
    
  @classmethod
  def _git_roots(clazz, files):
    roots = [ git.root(f) for f in files ]
    roots = [ r for r in roots if r ]
    return algorithm.unique(roots)

  @classmethod
  def _separate_files_and_filters(clazz, working_dir, arguments):
    files = []
    filter_descriptions = []
    for arg in arguments:
      normalized_path = file_path.normalize(path.join(working_dir, arg))
      if not path.exists(normalized_path):
        filter_descriptions.append(arg)
      else:
        files.append(arg)
    filters = [ unit_test_description.parse(f) for f in (filter_descriptions or []) ]
    return files, filters

  @classmethod
  def _resolve_files_and_dirs(clazz, working_dir, files_and_dirs):
    result = []
    for f in files_and_dirs:
      f = file_path.normalize(path.join(working_dir, f))
      if path.isfile(f):
        result += clazz._resolve_file(f)
      elif path.isdir(f):
        result += clazz._resolve_dir(f)
    result = algorithm.unique(result)
    result = [ path.normpath(r) for r in result ]
    return sorted(result)

  @classmethod
  def _resolve_dir(clazz, d):
    assert path.isdir(d)
    return file_finder.find_python_files(d)
#    return clazz._resolve_files_and_dirs(config)
    
  @classmethod
  def _resolve_file(clazz, f):
    assert path.isfile(f)
    return [ path.abspath(path.normpath(f)) ]

  def _test_for_file(self, finfo):
    if finfo.relative_filename.startswith('tests/'):
      return None
    name = path.splitext(path.basename(finfo.filename))[0]
    test_basename = 'test_%s.py' % (name)
    test_fragment = path.dirname(finfo.relative_filename)
    test_full_path = path.join(finfo.config.root_dir, 'tests', test_fragment, test_basename)
    if path.isfile(test_full_path):
      return file_info(self.config_env, test_full_path)
    return None

  def _tests_for_many_files(self, finfos):
    result = file_info_list()
    for finfo in finfos:
      test = self._test_for_file(finfo)
      if test:
        result.append(test)
    return result

  @classmethod
  def _resolve_tests_for_files(clazz, file_infos):
    result = []
    for f in files:
      test = clazz.test_for_file(f)
      if test:
        result.append(test)
    return result

  @classmethod
  def _find_root_of_roots(clazz, files):
    if not files:
      return None
    any_git_root = git.root(files[0])
    if any_git_root:
      return file_path.parent_dir(any_git_root)
    return False

  @classmethod
  def _make_filters_patterns(clazz, filters):
    patterns = []
    for f in filters:
      filename_pattern = None
      fixture_pattern = None
      function_pattern = None
      if f.filename:
        filename_pattern = clazz._make_fnmatch_pattern(f.filename)
      if f.fixture:
        fixture_pattern = clazz._make_fnmatch_pattern(f.fixture)
      if f.function:
        function_pattern = clazz._make_fnmatch_pattern(f.function)
      patterns.append(unit_test_description(filename_pattern, fixture_pattern, function_pattern))
    return patterns

  @classmethod
  def _make_fnmatch_pattern(clazz, pattern):
    pattern = pattern.lower()
    if clazz._is_fnmatch_pattern(pattern):
      return pattern
    return '*%s*' % (pattern)

  @classmethod
  def _is_fnmatch_pattern(clazz, pattern):
    for c in [ '*', '?', '[', ']', '!' ]:
      if pattern.count(c) > 0:
        return True
    return False
