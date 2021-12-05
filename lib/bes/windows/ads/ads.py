# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.fs.file_check import file_check
from bes.system.log import logger

from .ads_exe import ads_exe
from .ads_error import ads_error

class ads(object):
  'A class to deal with Windows NT Alternative Data Streams.'

  _log = logger('ads')

  @classmethod
  def has_stream(clazz, filename, stream_name):
    'Return True if filename has an attributed with key.'
    filename = file_check.check_file(filename)
    stream_name = clazz.check_stream_name(stream_name)

    ads_filename = clazz._make_ads_filename(filename, stream_name)
    return path.exists(ads_filename)
  
  @classmethod
  def check_stream_name(clazz, stream_name):
    if ':' in stream_name:
      raise ads_error('filename cannot contain \":\": {}'.format(stream_name))
    return stream_name
      
  @classmethod
  def _make_ads_filename(clazz, filename, stream_name):
    'Make an ADS filename from a regular filename.'
    check.check_string(filename)
    check.check_string(stream_name)
    
    basename = path.basename(filename)
    clazz.check_stream_name(basename)
    clazz.check_stream_name(stream_name)
    return '{}:{}'.format(filename, stream_name)
