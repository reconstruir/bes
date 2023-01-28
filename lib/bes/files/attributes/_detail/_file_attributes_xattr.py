#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import xattr

from bes.system.check import check
from bes.common.string_util import string_util
from bes.fs.file_check import file_check
from bes.system.execute import execute
from bes.system.host import host
from bes.system.log import logger

from bes.fs.file_attributes_base import file_attributes_base

class _file_attributes_xattr(file_attributes_base):

  _log = logger('_file_attributes_xattr')
  
  @classmethod
  #@abstractmethod
  def has_key(clazz, filename, key):
    'Return True if filename has an attributed with key.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)
    clazz.check_file_is_readable(filename)

    encoded_key = clazz._encode_key(key)
    return xattr.xattr(filename).has_key(encoded_key)
  
  @classmethod
  #@abstractmethod
  def get_bytes(clazz, filename, key):
    'Return the attribute value with key for filename.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)
    clazz.check_file_is_writable(filename)

    encoded_key = clazz._encode_key(key)
    if not xattr.xattr(filename).has_key(encoded_key):
      return None
    return xattr.getxattr(filename, encoded_key)
    
  @classmethod
  #@abstractmethod
  def set_bytes(clazz, filename, key, value):
    'Set the value of attribute with key to value for filename.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)
    check.check_bytes(value)
    clazz.check_file_is_writable(filename)

    clazz._log.log_method_d()

    encoded_key = clazz._encode_key(key)
    clazz._log.log_d(f'set_bytes:{filename}:{encoded_key}: calling xattr.setxattr with value "{value}"')
    rv = xattr.setxattr(filename, encoded_key, value)
    clazz._log.log_d(f'set_bytes:{filename}:{encoded_key}: xattr.setxattr returns with rv "{rv}"')
  
  @classmethod
  #@abstractmethod
  def remove(clazz, filename, key):
    'Remove the attirbute with key from filename.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)
    clazz.check_file_is_writable(filename)

    clazz._log.log_method_d()
    
    encoded_key = clazz._encode_key(key)
    xattr.removexattr(filename, encoded_key)
  
  @classmethod
  #@abstractmethod
  def keys(clazz, filename):
    'Return all the keys set for filename.'
    check.check_string(filename)
    clazz.check_file_is_readable(filename)

    raw_keys = [ key for key in xattr.xattr(filename).iterkeys() ]
    return sorted([ clazz._decode_key(key) for key in raw_keys ])
    
  @classmethod
  #@abstractmethod
  def clear(clazz, filename):
    'Create all attributes.'
    check.check_string(filename)
    clazz.check_file_is_writable(filename)

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
