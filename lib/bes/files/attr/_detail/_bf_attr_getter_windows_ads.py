#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system.check import check
from bes.files.bf_check import bf_check
from bes.system.log import logger
from bes.windows.ads.ads import ads
from bes.windows.ads.ads_error import ads_error

from ._bf_attr_getter_i import _bf_attr_getter_i
from ..bf_attr_getter_mixin import bf_attr_getter_mixin

class _bf_attr_getter_windows_ads(_bf_attr_getter_i, bf_attr_getter_mixin):
  'bf_attr implementation that uses windows ADS (alternative data streams)'
  
  _ADS_STREAM_NAME = 'bes_attributes'

  _log = logger('bf_attr')
  
  #@abstractmethod
  def has_key(self, filename, key):
    'Return True if filename has an attributed with key.'
    filename = bf_check.check_file(filename)
    key = self.check_key(key)
    bf_check.check_file_is_readable(filename)

    self._log.log_method_d()
    
    values = self._read_values(filename)
    self._log.log_d('has_key: values={}'.format(values))
    return values != None and key in values
 
  #@abstractmethod
  def get_bytes(self, filename, key):
    'Return the attribute value with key for filename.'
    filename = bf_check.check_file(filename)
    key = self.check_key(key)
    bf_check.check_file_is_readable(filename)

    values = self._read_values(filename)
    if not key in values:
      return None
    value = values.get(key)
    assert check.is_bytes(value)
    return value
    
  #@abstractmethod
  def set_bytes(self, filename, key, value):
    'Set the value of attribute with key to value for filename.'
    filename = bf_check.check_file(filename)
    key = self.check_key(key)
    check.check_bytes(value)
    bf_check.check_file_is_writable(filename)

    values = self._read_values(filename)
    self._log.log_d('set: before: values={}'.format(values))
    values[key] = value
    ads.write_values(filename, self._ADS_STREAM_NAME, values)
    self._log.log_d('set: wrote: values={}'.format(values))
    self._log.log_d('set: after: values={}'.format(self._read_values(filename)))
    
  #@abstractmethod
  def remove(self, filename, key):
    'Remove the attirbute with key from filename.'
    filename = bf_check.check_file(filename)
    key = self.check_key(key)
    bf_check.check_file_is_writable(filename)

    values = self._read_values(filename)
    if not key in values:
      return
    del values[key]
    ads.write_values(filename, self._ADS_STREAM_NAME, values)
  
  #@abstractmethod
  def keys(self, filename):
    'Return all the keys set for filename.'
    check.check_string(filename)
    bf_check.check_file_is_readable(filename)

    values = self._read_values(filename)
    return sorted([ key for key in values.keys() ])

  #@abstractmethod
  def clear(self, filename):
    'Create all attributes.'
    check.check_string(filename)
    bf_check.check_file_is_writable(filename)

    ads.write_values(filename, self._ADS_STREAM_NAME, {})

  @classmethod
  def _read_values(clazz, filename):
    try:
      values = ads.read_values(filename, clazz._ADS_STREAM_NAME)
      clazz._log.log_d('_read_values: values={}'.format(values))
      return values
    except ads_error as ex:
      return {}
