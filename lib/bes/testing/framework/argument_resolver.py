#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import algorithm
from bes.fs import file_ignore, file_path, file_util
from bes.git import git

from .config_env import config_env
from .file_finder import file_finder
from .unit_test_description import unit_test_description
from .unit_test_inspect import unit_test_inspect

class argument_resolver(object):

  FILE_IGNORE_FILENAME = '.bes_test_ignore'
  
  def __init__(self, working_dir, arguments):
    self.working_dir = path.abspath(working_dir)
    self.arguments = arguments
    self.file_ignore = file_ignore(self.FILE_IGNORE_FILENAME)
    self.files, self.filters = self._separate_files_and_filters(self.working_dir, self.arguments)
    resolved_files = self._resolve_files_and_dirs(self.working_dir, self.files)
    self.root_of_roots = self._find_root_of_roots(resolved_files)
    self.config_env = config_env(self.root_of_roots)
    resolved_files = self.file_ignore.filter_files(resolved_files)
    self.inspect_map = unit_test_inspect.inspect_map(resolved_files)

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
      print('F: %s' % (f))
      if path.isfile(f):
        result += clazz._resolve_file(f)
      elif path.isdir(f):
        result += clazz._resolve_dir(f)
    result += clazz.tests_for_many_files(result)
    result = algorithm.unique(result)
    result = [ path.normpath(r) for r in result ]
    return sorted(result)

  @classmethod
  def _resolve_dir(clazz, d):
    assert path.isdir(d)
#    config = clazz._read_config_file(d)
#    if config is None:
    return file_finder.find_python_files(d)
#    return clazz._resolve_files_and_dirs(config)
    
  @classmethod
  def _resolve_file(clazz, f):
    assert path.isfile(f)
    return [ path.abspath(path.normpath(f)) ]

  @classmethod
  def _read_config_file(clazz, d):
    p = path.join(d, '.bes_test_dirs')
    if not path.exists(p):
      return None
    content = file_util.read(p)
    lines = [ f for f in content.split('\n') if f ]
    files = [ path.join(d, f) for f in lines ]
    return sorted(algorithm.unique(files))
  
  @classmethod
  def test_for_file(clazz, filename):
    basename = path.basename(filename)
    dirname = path.dirname(filename)
    name = path.splitext(basename)[0]
    test_filename = 'test_%s.py' % (name)
    test_full_path = path.join(dirname, 'tests', test_filename)
    if path.exists(test_full_path):
      return test_full_path
    return None

  @classmethod
  def tests_for_many_files(clazz, files):
    result = []
    for f in files:
      test = clazz.test_for_file(f)
      if test:
        result.append(test)
    return result

  @classmethod
  def _apply_exclusions(clazz, files):
#    print('1 files: %s' % (files))
#    files = [ f for f in files if not f.endswith('bes_test.py') ]
#    print('2 files: %s' % (files))
#    files = [ f for f in files if 'test_data/bes.testing' not in f ]
#    print('3 files: %s' % (files))
#    files = [ f for f in files if not file_util.is_broken_link(f) ]
#    print('4 files: %s' % (files))
    return files

  @classmethod
  def _find_root_of_roots(clazz, files):
    if not files:
      return None
    any_git_root = git.root(files[0])
    if any_git_root:
      return file_path.parent_dir(any_git_root)
    return False
