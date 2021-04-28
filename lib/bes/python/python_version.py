#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check
from bes.version.software_version import software_version

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
  def check_version(clazz, version):
    'Check version is a x.y version or raise an error if not'
    check.check_string(version)

    if not clazz.is_version(version):
      raise python_error('Not a valid python version: "{}"'.format(version))
    return version
  
  @classmethod
  def is_full_version(clazz, full_version):
    'Return True if version is in the form major.minor.revision'
    check.check_string(full_version)
    
    sv = software_version.parse_version(full_version)
    return len(sv.parts) == 3

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
