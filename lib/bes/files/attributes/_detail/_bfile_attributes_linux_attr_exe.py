#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger
from bes.fs.file_check import file_check

from bes.linux.attr.linux_attr import linux_attr
from bes.linux.attr.linux_attr_error import linux_attr_error
from bes.linux.attr.linux_attr_error import linux_attr_permission_error

from bes.files.attributes.bfile_attributes_base import bfile_attributes_base

class _bfile_attributes_linux_attr_exe(bfile_attributes_base):

  _log = logger('_bfile_attributes_linux_attr_exe')
  
  @classmethod
  #@abstractmethod
  def has_key(clazz, filename, key):
    'Return True if filename has an attributed with key.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)
    clazz.check_file_is_readable(filename)

    return linux_attr.has_key(filename, key)

  @classmethod
  #@abstractmethod
  def get_bytes(clazz, filename, key):
    'Return the attribute value with key for filename.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)
    clazz.check_file_is_readable(filename)

    if not linux_attr.has_key(filename, key):
      return None
      
    return linux_attr.get_bytes(filename, key)
    
  @classmethod
  #@abstractmethod
  def set_bytes(clazz, filename, key, value):
    'Set the value of attribute with key to value for filename.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)
    check.check_bytes(value)
    clazz.check_file_is_writable(filename)

    clazz._log.log_method_d()

    linux_attr.set_bytes(filename, key, value)
  
  @classmethod
  #@abstractmethod
  def remove(clazz, filename, key):
    'Remove the attirbute with key from filename.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)
    clazz.check_file_is_writable(filename)
    
    linux_attr.remove(filename, key)
  
  @classmethod
  #@abstractmethod
  def keys(clazz, filename):
    'Return all the keys set for filename.'
    check.check_string(filename)
    clazz.check_file_is_readable(filename)

    return linux_attr.keys(filename)
    
  @classmethod
  #@abstractmethod
  def clear(clazz, filename):
    'Create all attributes.'
    check.check_string(filename)
    clazz.check_file_is_writable(filename)

    linux_attr.clear(filename)
