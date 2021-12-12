#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.common.string_util import string_util
from bes.system.execute import execute
from bes.system.host import host

import xattr

from ._file_attributes_base import _file_attributes_base
from .file_attributes_error import file_attributes_error
from .file_attributes_error import file_attributes_permission_error

class _file_attributes_xattr(_file_attributes_base):

  @classmethod
  #@abstractmethod
  def has_key(clazz, filename, key):
    'Return True if filename has an attributed with key.'
    return key in clazz.keys(filename)
  
  @classmethod
  #@abstractmethod
  def get(clazz, filename, key):
    'Return the attribute value with key for filename.'
    check.check_string(filename)
    check.check_string(key)
    try:
      return xattr.getxattr(filename, clazz._encode_key(key))
    except OSError as ex:
      return None
    except KeyError as ex:
      return None
    
  @classmethod
  #@abstractmethod
  def set(clazz, filename, key, value):
    'Set the value of attribute with key to value for filename.'
    try:
      xattr.setxattr(filename, clazz._encode_key(key), value)
    except IOError as ex:
      if ex.errno == 1 and 'Operation not permitted' in str(ex):
        raise file_attributes_permission_error(str(ex))
  
  @classmethod
  #@abstractmethod
  def remove(clazz, filename, key):
    'Remove the attirbute with key from filename.'
    check.check_string(filename)
    check.check_string(key)

    xattr.removexattr(filename, clazz._encode_key(key))
  
  @classmethod
  #@abstractmethod
  def keys(clazz, filename):
    'Return all the keys set for filename.'
    check.check_string(filename)
    return sorted([ clazz._decode_key(key) for key in xattr.xattr(filename).iterkeys() ])
    
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
    return clazz._decode_key(key.strip())

  @classmethod
  def _encode_key(clazz, key):
    if host.is_linux():
      return 'user.' + key
    return key

  @classmethod
  def _decode_key(clazz, key):
    if host.is_linux():
      key = string_util.remove_head(key, 'user.')
    return key
