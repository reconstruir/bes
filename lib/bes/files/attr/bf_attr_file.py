#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger
from bes.property.cached_class_property import cached_class_property

from .bf_attr import bf_attr
from .bf_attr_error import bf_attr_error

class bf_attr_file(object):

  _log = logger('bf_attr')

  def __init__(self, filename):
    self._filename = filename

  @cached_class_property
  def _bf_attr_instance(clazz):
    return bf_attr()
    
  @property
  def filename(self):
    return self._filename

  def has_key(self, key):
    return self._bf_attr_instance.has_key(self._filename, key)

  def get_bytes(self, key):
    return self._bf_attr_instance.get_bytes(self._filename, key)

  def set_bytes(self, key, value):
    self._bf_attr_instance.set_bytes(self._filename, key, value)

  def remove(self, key):
    self._bf_attr_instance.remove(self._filename, key)

  def keys(self):
    return self._bf_attr_instance.keys(self._filename)

  def clear(self):
    self._bf_attr_instance.clear(self._filename)

  def get_all(self):
    return self._bf_attr_instance.get_all(self._filename)

  def set_all(self, attributes):
    self._bf_attr_instance.set_all(self._filename, attributes)

  def get_string(self, key):
    return self._bf_attr_instance.get_string(self._filename, key)

  def set_string(self, key, value):
    self._bf_attr_instance.set_string(self._filename, key, value)

  def get_date(self, key):
    return self._bf_attr_instance.get_date(self._filename, key)

  def set_date(self, key, value):
    self._bf_attr_instance.set_date(self._filename, key, value)

  def get_bool(self, key):
    return self._bf_attr_instance.get_bool(self._filename, key)

  def set_bool(self, key, value):
    self._bf_attr_instance.set_bool(self._filename, key, value)
    
  def get_int(self, key):
    return self._bf_attr_instance.get_int(self._filename, key)

  def set_int(self, key, value):
    self._bf_attr_instance.set_int(self._filename, key, value)

  def get_float(self, key):
    return self._bf_attr_instance.get_float(self._filename, key)

  def set_float(self, key, value):
    self._bf_attr_instance.set_float(self._filename, key, value)
    
  def get_value(self, key):
    return self._bf_attr_instance.get_value(self._filename, key)

  def set_value(self, key, value):
    self._bf_attr_instance.set_value(self._filename, key, value)
    
  def __delitem__(self, key):
    if not self.has_key(key):
      raise bf_attr_error(f'No key "{key}" found for "{self.filename}"')
    self.remove(key)
  
  def __contains__(self, key):
    return self.has_key(key)
  
  def __getitem__(self, key):
    return self.get_value(key)

  def __setitem__(self, key, value):
    self.set_value(key, value)

check.register_class(bf_attr_file, include_seq = False)
