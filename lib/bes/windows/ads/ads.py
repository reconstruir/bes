# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path
import pickle

from bes.system.check import check
from bes.fs.file_check import file_check
from bes.fs.file_util import file_util
from bes.system.log import logger
from bes.system.log import logger

from .ads_error import ads_error

class ads(object):
  'A class to deal with Windows NT Alternative Data Streams.'

  _log = logger('ads')

  @classmethod
  def has_stream(clazz, filename, stream_name):
    'Return True if filename has stream_name.'
    filename = file_check.check_file(filename)
    stream_name = clazz.check_stream_name(stream_name)

    ads_filename = clazz._make_ads_filename(filename, stream_name)
    return path.exists(ads_filename)

  @classmethod
  def read_stream(clazz, filename, stream_name):
    'Return the content of stream_name for filename in bytes.'
    filename = file_check.check_file(filename)
    stream_name = clazz.check_stream_name(stream_name)

    ads_filename = clazz._make_ads_filename(filename, stream_name)
    try:
      with open(ads_filename, 'rb') as fp:
        return fp.read()
    except FileNotFoundError as ex:
      raise ads_error(str(ex))
    
  @classmethod
  def write_stream(clazz, filename, stream_name, value):
    'Write the content of stream_name for filename in bytes.'
    filename = file_check.check_file(filename)
    stream_name = clazz.check_stream_name(stream_name)
    check.check_bytes(value)
    
    ads_filename = clazz._make_ads_filename(filename, stream_name)
    clazz._log.log_d(f'write_stream: ads_filename={ads_filename} value={value}')
    with open(ads_filename, 'wb') as fp:
      fp.write(value)
      fp.flush()
      os.fsync(fp.fileno())

    assert value == clazz.read_stream(filename, stream_name)

  @classmethod
  def remove_stream(clazz, filename, stream_name):
    'Remove stream_name from filename if it exists.'
    filename = file_check.check_file(filename)
    stream_name = clazz.check_stream_name(stream_name)

    if not clazz.has_stream(filename, stream_name):
      return
    ads_filename = clazz._make_ads_filename(filename, stream_name)
    file_util.remove(ads_filename)
      
  @classmethod
  def check_stream_name(clazz, stream_name):
    if ':' in stream_name:
      raise ads_error('filename cannot contain \":\": {}'.format(stream_name))
    return stream_name

  @classmethod
  def write_values(clazz, filename, stream_name, values):
    'Write the content of stream_name for filename as values.'
    filename = file_check.check_file(filename)
    stream_name = clazz.check_stream_name(stream_name)
    check.check_dict(values)

    value = pickle.dumps(values)
    clazz.write_stream(filename, stream_name, value)
    assert value == clazz.read_stream(filename, stream_name)

  @classmethod
  def read_values(clazz, filename, stream_name):
    'Read the content of stream_name for filename as values.'
    filename = file_check.check_file(filename)
    stream_name = clazz.check_stream_name(stream_name)

    value = clazz.read_stream(filename, stream_name)
    if not value:
      return {}
    return pickle.loads(value)
    
  @classmethod
  def _make_ads_filename(clazz, filename, stream_name):
    'Make an ADS filename from a regular filename.'
    check.check_string(filename)
    check.check_string(stream_name)
    
    basename = path.basename(filename)
    clazz.check_stream_name(basename)
    clazz.check_stream_name(stream_name)
    return '{}:{}'.format(filename, stream_name)
