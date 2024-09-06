#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from .bf_attr2 import bf_attr2
from .bf_attr2_error import bf_attr2_error

class bf_attr2_file(object):

  _log = logger('bf_attr2_file')
  
  def __init__(self, filename):
    self._filename = filename

  @property
  def filename(self):
    return self._filename

  def has_key(self, key):
    return bf_attr2.has_key(self._filename, key)

  def get_bytes(self, key):
    return bf_attr2.get_bytes(self._filename, key)

  def set_bytes(self, key, value):
    bf_attr2.set_bytes(self._filename, key, value)

  def remove(self, key):
    bf_attr2.remove(self._filename, key)

  def keys(self):
    return bf_attr2.keys(self._filename)

  def clear(self):
    bf_attr2.clear(self._filename)

  def get_all(self):
    return bf_attr2.get_all(self._filename)

  def set_all(self, attributes):
    bf_attr2.set_all(self._filename, attributes)

  def get_string(self, key):
    return bf_attr2.get_string(self._filename, key)

  def set_string(self, key, value):
    bf_attr2.set_string(self._filename, key, value)

  def get_date(self, key):
    return bf_attr2.get_date(self._filename, key)

  def set_date(self, key, value):
    bf_attr2.set_date(self._filename, key, value)

  def get_bool(self, key):
    return bf_attr2.get_bool(self._filename, key)

  def set_bool(self, key, value):
    bf_attr2.set_bool(self._filename, key, value)
    
  def get_int(self, key):
    return bf_attr2.get_int(self._filename, key)

  def set_int(self, key, value):
    bf_attr2.set_int(self._filename, key, value)

  def get_float(self, key):
    return bf_attr2.get_float(self._filename, key)

  def set_float(self, key, value):
    bf_attr2.set_float(self._filename, key, value)
    
  def get_value(self, key):
    return bf_attr2.get_value(self._filename, key)

  def set_value(self, key, value):
    bf_attr2.set_value(self._filename, key, value)
    
  def __delitem__(self, key):
    if not self.has_key(key):
      raise bf_attr2_error(f'No key "{key}" found for "{self.filename}"')
    self.remove(key)
  
  def __contains__(self, key):
    return self.has_key(key)
  
  def __getitem__(self, key):
    return self.get_value(key)

  def __setitem__(self, key, value):
    self.set_value(key, value)

check.register_class(bf_attr2_file, include_seq = False)
