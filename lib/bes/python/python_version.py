#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check
from bes.version.software_version import software_version
from bes.version.semantic_version import semantic_version

from .python_error import python_error

class python_version(object):
  'Class to deal with python versions.'

  @classmethod
  def major_version(clazz, any_version):
    'Return x for x.y.z or x.y or x'
    check.check_string(any_version)
    
    sv = software_version.parse_version(any_version)
    if len(sv.parts) < 1:
      raise python_error('Invalid full python version: "{}"'.format(any_version))
    return str(sv.parts[0])

  @classmethod
  def version(clazz, any_version):
    'Return x.y for x.y.z or x.y'
    check.check_string(any_version)
    
    sv = software_version.parse_version(any_version)
    if len(sv.parts) < 2:
      raise python_error('Invalid python version: "{}"'.format(any_version))
    return '{}.{}'.format(sv.parts[0], sv.parts[1])
  
  @classmethod
  def is_version(clazz, version):
    'Return True if version is in the form major.minor'
    check.check_string(version)
    
    sv = software_version.parse_version(version)
    return len(sv.parts) == 2

  @classmethod
  def is_full_version(clazz, full_version):
    'Return True if version is in the form major.minor.revision'
    check.check_string(full_version)
    
    sv = software_version.parse_version(full_version)
    return len(sv.parts) == 3

  @classmethod
  def is_major_version(clazz, major_version):
    'Return True if version is in the form major'
    check.check_string(major_version)
    
    sv = software_version.parse_version(version)
    return len(sv.parts) == 1

  @classmethod
  def check_version(clazz, version):
    'Check version is a x.y version or raise an error if not'
    check.check_string(version)

    if not clazz.is_version(version):
      raise python_error('Not a valid python version: "{}"'.format(version))
    return version
  
  @classmethod
  def check_full_version(clazz, version):
    'Check version is a x.y.z version or raise an error if not'
    check.check_string(version)

    if not clazz.is_full_version(version):
      raise python_error('Not a valid python full version: "{}"'.format(version))
    return version
  
  _parsed_version = namedtuple('_parsed_version', 'major, minor, revision')
  @classmethod
  def parse(clazz, any_version):
    'Return the python version parts as ints'
    check.check_string(any_version)

    sv = software_version.parse_version(any_version)
    parts = list(sv.parts)
    major = None
    minor = None
    revision = None
    if parts:
      major = parts.pop(0)
    if parts:
      minor = parts.pop(0)
    if parts:
      revision = parts.pop(0)
    return clazz._parsed_version(major, minor, revision)

  @classmethod
  def filter_by_version(clazz, full_version_list, version):
    check.check_string_seq(full_version_list)
    clazz.check_version(version)

    result = []
    for next_full_version in full_version_list:
      if not clazz.is_full_version(next_full_version):
        raise python_error('Not a python full version: "{}"'.format(next_full_version))
      if python_version.version(next_full_version) == version:
        result.append(next_full_version)
    return result

  @classmethod
  def filter_by_major_version(clazz, full_version_list, major_version):
    check.check_string_seq(full_version_list)
    clazz.check_major_version(major_version)

    result = []
    for next_full_version in full_version_list:
      if not clazz.is_full_version(next_full_version):
        raise python_error('Not a python full version: "{}"'.format(next_full_version))
      if python_version.major_version(next_full_version) == major_version:
        result.append(next_full_version)
    return result
  
  @classmethod
  def compare_full_versions(clazz, full_version1, full_version2):
    check.check_full_version(full_version1)
    check.check_full_version(full_version2)

    v1 = semantic_version(full_version1)
    v2 = semantic_version(full_version2)
    return v1.compare(v2)
