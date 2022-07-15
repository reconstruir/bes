#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import fnmatch, os.path as path

from bes.compat.StringIO import StringIO
from bes.common.algorithm import algorithm
from bes.system.check import check
from bes.common.type_checked_list import type_checked_list

from .file_info import file_info
from .pytest import pytest

class file_info_list(type_checked_list):

  __value_type__ = file_info
  
  def __init__(self, values = None):
    super(file_info_list, self).__init__(values = values)
  
  def to_string(self):
    buf = StringIO()
    first = True
    for finfo in iter(self):
      if not first:
        buf.write('\n')
      first = False
      buf.write(str(finfo))
    return buf.getvalue()
    
  def __str__(self):
    return self.to_string()

  def make_inspect_map(self):
    files = [ finfo.filename for finfo in self ]
    tests = pytest.inspect_files(files)
    result = {}
    for test in tests:
      if not test.filename in result:
        result[test.filename] = []
      result[test.filename].append(test)
    return result

  def remove_dups(self):
    self._values = self._unique_list(self._values)
    
  @classmethod
  def _unique_list(clazz, infos):
    'Return a list of file infos with duplicates removed.'
    check.check_list(infos, file_info)
    result = []
    seen = set()
    for info in infos:
      if info.filename not in seen:
        seen.add(info.filename)
        result.append(info)
    return result

  @classmethod
  def _match_test(clazz, patterns, filename):
    filename = filename.lower()
    for pattern in patterns:
      pattern = pattern.lower()
      if fnmatch.fnmatch(filename, pattern):
        return True
      if fnmatch.fnmatch(path.basename(filename), pattern):
        return True
    return False

  def _match_filenames(self, patterns):
    result = file_info_list()
    for finfo in iter(self):
      if self._match_test(patterns, finfo.filename):
        result.append(finfo)
    result.remove_dups()
    return result

  def filter_by_filenames(self, patterns):
    check.check_unit_test_description_seq(patterns)
    filename_patterns = [ p.filename for p in patterns if p.filename ]
    if not filename_patterns:
      return file_info_list(self._values)
    return self._match_filenames(filename_patterns)

  def filter_by_test_filename_only(self):
    result = file_info_list()
    for finfo in iter(self):
      filename = path.basename(finfo.filename).lower()
      if filename.startswith('test_')  and filename.endswith('.py'):
        result.append(finfo)
    result.remove_dups()
    return result

#    # FIXME: change to ignore_without_tests()
#    file_infos = file_info_list([ f for f in file_infos if f.filename in self.inspect_map ])
#    # FIXME: change to filter_with_patterns_tests()
#    file_infos = file_infos.filter_by_filenames(filter_patterns)
  
check.register_class(file_info_list, include_seq = False)
