#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import algorithm
from bes.fs import file_path
from bes.git import git
from .file_finder import file_finder

from .unit_test_description import unit_test_description

class argument_resolver(object):

  def __init__(self, root_dir, arguments):
    self.root_dir = path.abspath(root_dir)
    self.arguments = arguments
    self.files, self.filters = self._separate_files_and_filters(self.root_dir, self.arguments)
#    print('files: %s' % (self.files))
#    print('filters: %s' % (self.filters))
    self.resolved_files = self._resolve_files_and_dirs(self.root_dir, self.files)
    
#    print('resolved_files: %s' % (self.resolved_files))

  @classmethod
  def _git_roots(clazz, files):
    roots = [ git.root(f) for f in files ]
    roots = [ r for r in roots if r ]
    return algorithm.unique(roots)

  @classmethod
  def _separate_files_and_filters(clazz, root_dir, arguments):
    files = []
    filter_descriptions = []
    for arg in arguments:
      normalized_path = file_path.normalize(path.join(root_dir, arg))
      if not path.exists(normalized_path):
        filter_descriptions.append(arg)
      else:
        files.append(arg)
    filters = [ unit_test_description.parse(f) for f in (filter_descriptions or []) ]
    return files, filters

  @classmethod
  def _resolve_files_and_dirs(clazz, root_dir, files_and_dirs):
    result = []
    for f in files_and_dirs:
      f = file_path.normalize(path.join(root_dir, f))
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
