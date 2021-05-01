#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#
class dim_python(object):
  'Python constants.'

  PYTHON_VERSIONS = (
    '2.7',
    '3.7',
    '3.8',
  )

  DEFAULT_PYTHON_VERSION = '3.7'
  
  @classmethod
  def python_version_is_valid(clazz, python_version):
    return python_version in clazz.PYTHON_VERSIONS

  @classmethod
  def check_python_version(clazz, python_version):
    if not clazz.python_version_is_valid(python_version):
      raise ValueError('Invalid python_version: "{}" - should be one of {}'.format(python_version, ' '.join(clazz.PYTHON_VERSIONS)))
    return python_version
  
  @classmethod
  def resolve_python_versions(clazz, python_versions):
    if not python_versions:
      return [ clazz.DEFAULT_PYTHON_VERSION ]
    return sorted(python_versions)
