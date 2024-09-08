#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger
from bes.files.bf_check import bf_check

from bes.linux.attr.linux_attr import linux_attr
from bes.linux.attr.linux_attr_error import linux_attr_error
from bes.linux.attr.linux_attr_error import linux_attr_permission_error

from ._bf_attr2_getter_i import _bf_attr2_getter_i
from ..bf_attr2_getter_mixin import bf_attr2_getter_mixin

class _bf_attr2_getter_linux_attr_exe(_bf_attr2_getter_i, bf_attr2_getter_mixin):

  #@abstractmethod
  def has_key(self, filename, key):
    'Return True if filename has an attributed with key.'
    filename = bf_check.check_file(filename)
    key = self.check_key(key)
    bf_check.check_file_is_readable(filename)

    return linux_attr.has_key(filename, key)

  #@abstractmethod
  def get_bytes(self, filename, key):
    'Return the attribute value with key for filename.'
    filename = bf_check.check_file(filename)
    key = self.check_key(key)
    bf_check.check_file_is_readable(filename)

    if not linux_attr.has_key(filename, key):
      return None
      
    return linux_attr.get_bytes(filename, key)
    
  #@abstractmethod
  def set_bytes(self, filename, key, value):
    'Set the value of attribute with key to value for filename.'
    filename = bf_check.check_file(filename)
    key = self.check_key(key)
    check.check_bytes(value)
    bf_check.check_file_is_writable(filename)

    self._log.log_method_d()

    linux_attr.set_bytes(filename, key, value)
  
  #@abstractmethod
  def remove(self, filename, key):
    'Remove the attirbute with key from filename.'
    filename = bf_check.check_file(filename)
    key = self.check_key(key)
    bf_check.check_file_is_writable(filename)
    
    linux_attr.remove(filename, key)
  
  #@abstractmethod
  def keys(self, filename):
    'Return all the keys set for filename.'
    check.check_string(filename)
    bf_check.check_file_is_readable(filename)

    return linux_attr.keys(filename)
    
  #@abstractmethod
  def clear(self, filename):
    'Create all attributes.'
    check.check_string(filename)
    bf_check.check_file_is_writable(filename)

    linux_attr.clear(filename)
