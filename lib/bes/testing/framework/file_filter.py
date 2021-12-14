#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import fnmatch, os.path as path
from collections import namedtuple
from bes.common.algorithm import algorithm
from bes.common.check import check

class file_filter(object):
  test_descriptor = namedtuple('test_descriptor', 'file_info,tests')

  @classmethod
  def filter_files(clazz, finfos, patterns):
    check.check_file_info_list(finfos)
    if not patterns:
      return [ clazz.test_descriptor(finfo, None) for finfo in finfos ]
    result = []
    for finfo in finfos:
      #assert False
      matching_tests = clazz._matching_tests(finfo.inspection, patterns)
      if matching_tests:
        result.append(clazz.test_descriptor(finfo, matching_tests))
    return result
  
  @classmethod
  def _matching_tests(clazz, inspection, patterns):
    result = []
    for test in inspection:
      for pattern in patterns:
        fixture_matches = True
        if pattern.fixture:
          fixture_matches = fnmatch.fnmatch(test.fixture.lower(), pattern.fixture.lower())
        function_matches = True
        if pattern.function:
          function_matches = fnmatch.fnmatch(test.function.lower(), pattern.function.lower())
        if fixture_matches and function_matches:
          result.append(test)
    return result

  @classmethod
  def ignore_files(clazz, filtered_files, ignore_patterns):
    return [ f for f in filtered_files if not clazz.filename_matches_any_pattern(f.file_info.filename, ignore_patterns) ]

#  @classmethod
#  def filenames(clazz, filtered_files):
#    return sorted([ f.file_info for f in filtered_files ])

#  @classmethod
#  def common_prefix(clazz, filtered_files):
#    return path.commonprefix([f.filename for f in filtered_files]).rpartition(os.sep)[0]
  
  @classmethod
  def filename_matches_any_pattern(clazz, filename, patterns):
    for pattern in patterns:
      if fnmatch.fnmatch(filename, pattern):
        return True
    return False
  
  @classmethod
  def env_dirs(clazz, filtered_files):
    filenames = [ f.filename for f in filtered_files ]
    roots = [ clazz._test_file_get_root(f) for f in filenames ]
    roots = algorithm.unique(roots)
    roots = [ f for f in roots if f ]
    result = []
    for root in roots:
      env_dir = path.join(root, 'env')
      if path.isdir(env_dir):
        result.append(env_dir)
    return result
  
  @classmethod
  def _test_file_get_root(clazz, filename):
    if '/lib/' in filename:
      return filename.partition('/lib')[0]
    elif '/bin/' in filename:
      return filename.partition('/bin')[0]
    else:
      return None
