#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import os
from bes.common.check import check
from bes.fs.file_check import file_check
from bes.key_value.key_value_list import key_value_list

from ._file_attributes_base import _file_attributes_base

class _file_attributes_windows(_file_attributes_base):
  'file_attributes implementation that uses windows ADS (alternative data streams)'
  
  _ADS_STREAM_NAME = 'bes_attributes'
  
  @classmethod
  #@abstractmethod
  def get(clazz, filename, key):
    'Return the attribute value with key for filename.'
    check.check_string(filename)
    check.check_string(key)
    file_check.check_file(filename)
    clazz._check_key(key)
    values = clazz._read_values(filename, clazz._ADS_STREAM_NAME)
    if not values:
      return None
    return values.get(key, None)
    
  @classmethod
  #@abstractmethod
  def set(clazz, filename, key, value):
    'Set the value of attribute with key to value for filename.'
    check.check_string(filename)
    check.check_string(key)
    check.check_string(value)
    file_check.check_file(filename)
    clazz._check_key(key)
    values = clazz._read_values(filename, clazz._ADS_STREAM_NAME) or {}
    values[key] = value
    clazz._write_values(filename, clazz._ADS_STREAM_NAME, values)
    
  @classmethod
  #@abstractmethod
  def remove(clazz, filename, key):
    'Remove the attirbute with key from filename.'
    check.check_string(filename)
    check.check_string(key)
    file_check.check_file(filename)
    clazz._check_key(key)
    values = clazz._read_values(filename, clazz._ADS_STREAM_NAME) or {}
    if not key in values:
      return
    del values[key]
    clazz._write_values(filename, clazz._ADS_STREAM_NAME, values)
  
  @classmethod
  #@abstractmethod
  def keys(clazz, filename):
    'Return all the keys set for filename.'
    file_check.check_file(filename)
    values = clazz._read_values(filename, clazz._ADS_STREAM_NAME) or {}
    return sorted([ key for key in values.keys() ])

  @classmethod
  #@abstractmethod
  def clear(clazz, filename):
    'Create all attributes.'
    check.check_string(filename)
    file_check.check_file(filename)
    clazz._write_values(filename, clazz._ADS_STREAM_NAME, {})

  @classmethod
  def _read_values(clazz, filename, stream_name):
    'Read key values from the windows ADS (alternate data stream).'
    ads_filename = clazz._make_ads_filename(filename, stream_name)
    try:
      with open(ads_filename, 'rb') as fp:
        content = fp.read().decode('utf-8')
        fp.close()
        return key_value_list.parse(content).to_dict()
    except FileNotFoundError as ex:
      return None
      
  @classmethod
  def _write_values(clazz, filename, stream_name, values):
    'Write key values from the windows ADS'
    check.check_dict(values)
    ads_filename = clazz._make_ads_filename(filename, stream_name)
    content = key_value_list.from_dict(values).to_string(value_delimiter = '\r\n').encode('utf-8')
    with open(ads_filename, 'wb') as fp:
      fp.write(content)
      fp.write(b'\r\n')
      fp.close()
    
  @classmethod
  def _make_ads_filename(clazz, filename, stream_name):
    'Make an ADS filename from a regular filename.'
    basename = path.basename(filename)
    if ':' in basename:
      raise ValueError('filename cannot contain \":\": {}'.format(filename))
    if ':' in stream_name:
      raise ValueError('stream_name cannot contain \":\": {}'.format(stream_name))
    return '{}:{}'.format(filename, stream_name)
