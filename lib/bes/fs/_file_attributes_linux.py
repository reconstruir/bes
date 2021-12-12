#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.system.log import logger
from bes.fs.file_check import file_check

from bes.linux.attr.linux_attr import linux_attr
from bes.linux.attr.linux_attr_error import linux_attr_error
from bes.linux.attr.linux_attr_error import linux_attr_permission_error

from ._file_attributes_base import _file_attributes_base
from .file_attributes_error import file_attributes_error
from .file_attributes_error import file_attributes_permission_error

class _file_attributes_linux(_file_attributes_base):

  _log = logger('_file_attributes_linux')
  
  @classmethod
  #@abstractmethod
  def has_key(clazz, filename, key):
    'Return True if filename has an attributed with key.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)

    return linux_attr.has_key(filename, key)

  @classmethod
  #@abstractmethod
  def get(clazz, filename, key):
    'Return the attribute value with key for filename.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)

    try:
      return linux_attr.get_bytes(filename, key)
    except linux_attr_error as ex:
      return None
    
  @classmethod
  #@abstractmethod
  def set(clazz, filename, key, value):
    'Set the value of attribute with key to value for filename.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)
    check.check_bytes(value)

    clazz._log.log_method_d()

    try:
      linux_attr.set_bytes(filename, key, value)
    except linux_attr_permission_error as ex:
      raise file_attributes_permission_error(ex.message)
  
  @classmethod
  #@abstractmethod
  def remove(clazz, filename, key):
    'Remove the attirbute with key from filename.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)
    
    try:
      linux_attr.remove(filename, key)
    except linux_attr_error as ex:
      raise file_attributes_error(ex.message)
  
  @classmethod
  #@abstractmethod
  def keys(clazz, filename):
    'Return all the keys set for filename.'
    check.check_string(filename)

    try:
      return linux_attr.keys(filename)
    except linux_attr_error as ex:
      raise file_attributes_error(ex.message)
    
  @classmethod
  #@abstractmethod
  def clear(clazz, filename):
    'Create all attributes.'
    check.check_string(filename)

    try:
      linux_attr.clear(filename)
    except linux_attr_error as ex:
      raise file_attributes_error(ex.message)
