#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system.check import check
from bes.fs.file_check import file_check
from bes.system.log import logger
from bes.windows.ads.ads import ads
from bes.windows.ads.ads_error import ads_error

from bes.files.attributes.bfile_attributes_base import bfile_attributes_base

class _bfile_attributes_windows_ads(bfile_attributes_base):
  'bfile_attributes implementation that uses windows ADS (alternative data streams)'
  
  _ADS_STREAM_NAME = 'bes_attributes'

  _log = logger('_bfile_attributes_windows_ads')
  
  @classmethod
  #@abstractmethod
  def has_key(clazz, filename, key):
    'Return True if filename has an attributed with key.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)
    clazz.check_file_is_readable(filename)

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
    clazz.check_file_is_readable(filename)

    values = clazz._read_values(filename)
    if not key in values:
      return None
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
    clazz.check_file_is_writable(filename)

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
    clazz.check_file_is_writable(filename)

    values = clazz._read_values(filename)
    if not key in values:
      return
    del values[key]
    ads.write_values(filename, clazz._ADS_STREAM_NAME, values)
  
  @classmethod
  #@abstractmethod
  def keys(clazz, filename):
    'Return all the keys set for filename.'
    check.check_string(filename)
    clazz.check_file_is_readable(filename)

    values = clazz._read_values(filename)
    return sorted([ key for key in values.keys() ])

  @classmethod
  #@abstractmethod
  def clear(clazz, filename):
    'Create all attributes.'
    check.check_string(filename)
    clazz.check_file_is_writable(filename)

    ads.write_values(filename, clazz._ADS_STREAM_NAME, {})

  @classmethod
  def _read_values(clazz, filename):
    try:
      values = ads.read_values(filename, clazz._ADS_STREAM_NAME)
      clazz._log.log_d('_read_values: values={}'.format(values))
      return values
    except ads_error as ex:
      return {}
