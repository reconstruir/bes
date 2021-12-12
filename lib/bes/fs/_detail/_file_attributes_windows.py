#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.fs.file_check import file_check
from bes.system.log import logger
from bes.windows.ads.ads import ads
from bes.windows.ads.ads_error import ads_error

from bes.fs.file_attributes_base import file_attributes_base
from bes.fs.file_attributes_error import file_attributes_error

class _file_attributes_windows(file_attributes_base):
  'file_attributes implementation that uses windows ADS (alternative data streams)'
  
  _ADS_STREAM_NAME = 'bes_attributes'

  _log = logger('_file_attributes_windows')
  
  @classmethod
  #@abstractmethod
  def has_key(clazz, filename, key):
    'Return True if filename has an attributed with key.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)

    clazz._log.log_method_d()
    
    values = clazz._read_values(filename)
    clazz._log.log_d('has_key: values={}'.format(values))
    return values != None and key in values
 
  @classmethod
  #@abstractmethod
  def get_bytes(clazz, filename, key):
    'Return the attribute value with key for filename.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)

    values = clazz._read_values(filename)
    if not key in values:
      return None #raise file_attributes_error('Key not found: {}'.format(key))
    value = values.get(key)
    assert check.is_bytes(value)
    return value
    
  @classmethod
  #@abstractmethod
  def set_bytes(clazz, filename, key, value):
    'Set the value of attribute with key to value for filename.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)
    check.check_bytes(value)

    values = clazz._read_values(filename)
    clazz._log.log_d('set: before: values={}'.format(values))
    values[key] = value
    ads.write_values(filename, clazz._ADS_STREAM_NAME, values)
    clazz._log.log_d('set: wrote: values={}'.format(values))
    clazz._log.log_d('set: after: values={}'.format(clazz._read_values(filename)))
    
  @classmethod
  #@abstractmethod
  def remove(clazz, filename, key):
    'Remove the attirbute with key from filename.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)

    values = clazz._read_values(filename)
    if not key in values:
      return
    del values[key]
    ads.write_values(filename, clazz._ADS_STREAM_NAME, values)
  
  @classmethod
  #@abstractmethod
  def keys(clazz, filename):
    'Return all the keys set for filename.'
    filename = file_check.check_file(filename)

    values = clazz._read_values(filename)
    return sorted([ key for key in values.keys() ])

  @classmethod
  #@abstractmethod
  def clear(clazz, filename):
    'Create all attributes.'
    check.check_string(filename)
    filename = file_check.check_file(filename)

    ads.write_values(filename, clazz._ADS_STREAM_NAME, {})

  @classmethod
  def _read_values(clazz, filename):
    try:
      values = ads.read_values(filename, clazz._ADS_STREAM_NAME)
      clazz._log.log_d('_read_values: values={}'.format(values))
      return values
    except ads_error as ex:
      return {}
