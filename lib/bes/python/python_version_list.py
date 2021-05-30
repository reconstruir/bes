#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check
from bes.version.semantic_version import semantic_version
from bes.property.cached_property import cached_property
from bes.common.type_checked_list import type_checked_list

from .python_error import python_error
from .python_version import python_version

class python_version_list(type_checked_list):

  __value_type__ = python_version
  
  def __init__(self, values = None):
    super(python_version_list, self).__init__(values = values)

  @classmethod
  def cast_value(clazz, value):
    if check.is_string(value):
      return python_version(value)
    return value
    
  def sort(self, reverse = False):
    self._values = sorted(self._values, key = lambda v: v._ver._tokens, reverse = reverse)

  def is_full_version(self):
    for value in self:
      if not value.is_full_version():
        return False
    return True
    
  def filter_by_version(self, version):
    check.check_python_version(version)

    result = python_version_list()
    if version.is_full_version():
      result.extend([ v for v in self if v.is_full_version() and v == version ])
    elif version.is_version():
      result.extend([ v for v in self if len(v) >= 2 and v.version == version ])
    elif version.is_major_version():
      result.extend([ v for v in self if len(v) >= 1 and v.major_version == version ])
    result.sort()
    return result

  def _make_version_map(self):
    'Return a map of versions to list of all available full versions'
    result = {}
    for v in self:
      key = str(v.version)
      if not key in result:
        result[key] = python_version_list()
      result[key].append(v)
    for _, available_versions in result.items():
      available_versions.sort()
    return result

  def make_availability_list(self, num_per_version):
    'Return an availability list of newest versions for each major.minor version'
    result = python_version_list()
    version_map = self._make_version_map()
    for version, available_versions in version_map.items():
      available_versions.sort(reverse = True)
      limited_versions = available_versions[0 : num_per_version]
      result.extend(limited_versions)
    result.sort()
    return result
  
check.register_class(python_version_list, include_seq = False)
