#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..common.algorithm import algorithm
from ..property.cached_class_property import cached_class_property
from ..system.check import check
from ..system.log import logger
from ..testing.unit_test_function_skip import unit_test_function_skip
from ..version.semantic_version import semantic_version

from .python_exe import python_exe
from .python_version import python_version
from .python_error import python_error

class python_discovery(object):
  'Class to deal with discovering specific versions of python.'

  _log = logger('python_discovery')

  @cached_class_property
  def _all_exes_info(clazz):
    # The python 3.8 that comes with xcode is very non standard
    # crapping all kinds of droppings in non standard places such
    # as ~/Library/Caches even though the --no-cache-dir was given
    # so never use them for tests since they create side effects
    infos = python_exe.find_all_exes_info(exclude_sources = ( 'xcode', ))
    if not infos:
      raise python_error('No pythons found in this system')
    return infos

  @cached_class_property
  def _all_exes_items_sorted(clazz):
    return sorted(clazz._all_exes_info.items(), key = lambda item: item[1].version, reverse = True)

  @classmethod
  def find_by_version(clazz, version):
    check.check_string(version)

    return clazz._match(lambda info: info.version == version, None)
    
  @classmethod
  def find_by_full_version(clazz, full_version):
    check.check_string(full_version)

    return clazz._match(lambda info: info.full_version == full_version, None)

  @classmethod
  def find_by_major_version(clazz, major_version):
    check.check_int(major_version)

    return clazz._match(lambda info: info.major_version == major_version, None)
  
  @classmethod
  def _match(clazz, condition, default_value):
    return next((exe for exe, info in clazz._all_exes_items_sorted if condition(info)), default_value)
  
  @classmethod
  def dump(clazz):
    for exe, info in clazz._all_exes_items_sorted:
      print(f'{exe}: {info.version} {info.full_version}')

  @classmethod
  def all_exes(clazz):
    return [ exe for exe, _ in clazz._all_exes_items_sorted ]

  @classmethod
  def all_versions(clazz):
    return algorithm.unique([ info.version for _, info in clazz._all_exes_items_sorted ])
  
  @classmethod
  def any_exe(clazz):
    return clazz._all_exes_items_sorted[0][1].exe
