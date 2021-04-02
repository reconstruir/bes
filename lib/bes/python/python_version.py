#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

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
  def is_full_version(clazz, full_version):
    'Return True if version is in the form major.minor.revision'
    check.check_string(full_version)
    
    sv = software_version.parse_version(full_version)
    return len(sv.parts) == 3
