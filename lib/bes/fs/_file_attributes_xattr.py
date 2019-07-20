#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.system.execute import execute

import xattr

from ._file_attributes_base import _file_attributes_base

class _file_attributes_xattr(_file_attributes_base):

  @classmethod
  #@abstractmethod
  def get(clazz, filename, key):
    'Return the attribute value with key for filename.'
    check.check_string(filename)
    check.check_string(key)
    try:
      return xattr.getxattr(filename, key)
    except KeyError as ex:
      return None
    
  @classmethod
  #@abstractmethod
  def set(clazz, filename, key, value):
    'Set the value of attribute with key to value for filename.'
    xattr.setxattr(filename, key, value)
  
  @classmethod
  #@abstractmethod
  def remove(clazz, filename, key):
    'Remove the attirbute with key from filename.'
    check.check_string(filename)
    check.check_string(key)
    xattr.removexattr(filename, key)
  
  @classmethod
  #@abstractmethod
  def keys(clazz, filename):
    'Return all the keys set for filename.'
    check.check_string(filename)
    return sorted([ key for key in xattr.xattr(filename).iterkeys() ])
    
  @classmethod
  #@abstractmethod
  def clear(clazz, filename):
    'Create all attributes.'
    check.check_string(filename)
    xattr.xattr(filename).clear()
  
  @classmethod
  def _parse_key(clazz, s):
    'Return all the keys set for filename.'
    s = s.strip()
    if not s:
      return None
    key, delim, value = s.partition(':')
    assert delim == ':'
    return key.strip()
