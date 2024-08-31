#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger
from bes.files.bf_check import bf_check

from bes.macos.xattr_exe.xattr_exe import xattr_exe
from bes.macos.xattr_exe.xattr_exe_error import xattr_exe_error
from bes.macos.xattr_exe.xattr_exe_error import xattr_exe_permission_error

from ._bf_attr_i import _bf_attr_i

class _bf_attr_macos_xattr_exe(_bf_attr_i):

  _log = logger('_bf_attr_macos_xattr_exe')
  
  @classmethod
  #@abstractmethod
  def has_key(clazz, filename, key):
    'Return True if filename has an attributed with key.'
    filename = bf_check.check_file(filename)
    key = clazz.check_key(key)
    bf_check.check_file_is_readable(filename)
    
    return xattr_exe.has_key(filename, key)

  @classmethod
  #@abstractmethod
  def get_bytes(clazz, filename, key):
    'Return the attribute value with key for filename.'
    filename = bf_check.check_file(filename)
    key = clazz.check_key(key)
    bf_check.check_file_is_readable(filename)

    if not xattr_exe.has_key(filename, key):
      return None
    
    return xattr_exe.get_bytes(filename, key)
    
  @classmethod
  #@abstractmethod
  def set_bytes(clazz, filename, key, value):
    'Set the value of attribute with key to value for filename.'
    filename = bf_check.check_file(filename)
    key = clazz.check_key(key)
    check.check_bytes(value)
    bf_check.check_file_is_writable(filename)

    clazz._log.log_method_d()
    xattr_exe.set_bytes(filename, key, value)
  
  @classmethod
  #@abstractmethod
  def remove(clazz, filename, key):
    'Remove the attirbute with key from filename.'
    filename = bf_check.check_file(filename)
    key = clazz.check_key(key)
    bf_check.check_file_is_writable(filename)
    
    xattr_exe.remove(filename, key)
  
  @classmethod
  #@abstractmethod
  def keys(clazz, filename):
    'Return all the keys set for filename.'
    check.check_string(filename)
    bf_check.check_file_is_readable(filename)

    return xattr_exe.keys(filename)
    
  @classmethod
  #@abstractmethod
  def clear(clazz, filename):
    'Create all attributes.'
    check.check_string(filename)
    bf_check.check_file_is_writable(filename)

    xattr_exe.clear(filename)
