#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import fnmatch
from .file_info import file_info
from bes.common import algorithm, check, type_checked_list

class file_info_list(type_checked_list):

  __value_type__ = file_info
  
  def __init__(self, values = None):
    super(file_info_list, self).__init__(values = values)

#  def __contains__(self, v):
#    if check.is_string(v):
#      return self.contains_key(v)
#    return super(file_info_list, self).__contains__(v)
  
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
    result = {}
    for finfo in iter(self):
      assert finfo.filename not in result
      if finfo.inspection:
        result[finfo.filename] = finfo.inspection
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
      if fnmatch.fnmatch(filename, pattern.lower()):
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

#    # FIXME: change to ignore_without_tests()
#    file_infos = file_info_list([ f for f in file_infos if f.filename in self.inspect_map ])
#    # FIXME: change to filter_with_patterns_tests()
#    file_infos = file_infos.filter_by_filenames(filter_patterns)
  
check.register_class(file_info_list, include_seq = False)
