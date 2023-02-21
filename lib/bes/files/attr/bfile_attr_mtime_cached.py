#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check
from bes.system.log import logger

from ..bfile_date import bfile_date
from ..bfile_check import bfile_check

from .bfile_attr import bfile_attr
from .bfile_attr_error import bfile_attr_error

class bfile_attr_mtime_cached(bfile_attr):

  _log = logger('attr_mtime_cached')
  
  @classmethod
  def get_cached_bytes(clazz, filename, key, value_maker):
    'Return the attribute value with key for filename as bytes.'
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    check.check_callable(value_maker)

    value, _, _, _ = clazz._do_get_cached_bytes(filename, key, value_maker)
    return value

  @classmethod
  def _make_mtime_key(clazz, key):
    return f'__bes_mtime_{key}__'

  _get_cached_bytes_result = namedtuple('_get_cached_bytes_result', 'value, mtime, mtime_key, is_cached')
  @classmethod
  def _do_get_cached_bytes(clazz, filename, key, value_maker):
    'Return the attribute value with key for filename as bytes.'
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    check.check_callable(value_maker)

    clazz._log.log_method_d()

    
    mtime_key = clazz._make_mtime_key(key)
    attr_mtime = clazz.get_date(filename, mtime_key)
    file_mtime = bfile_date.get_modification_date(filename)
    value = None
    
    label = f'_do_get_cached_bytes:{filename}:{key}'

    clazz._log.log_d(f'{label}: attr_mtime={attr_mtime} file_mtime={file_mtime}')
    
    if file_mtime == attr_mtime:
      value = clazz.get_bytes(filename, key)
      clazz._log.log_d(f'{label}: 1: value={value}')
      return clazz._get_cached_bytes_result(value, file_mtime, mtime_key, True)

    value = value_maker(filename)
    if value == None:
      raise bfile_attr_error(f'value should never be None')

    clazz._log.log_d(f'{label}: 3: value={value}')
    clazz.set_bytes(filename, key, value)
    #file_mtime = bfile_date.get_modification_date(filename)
    clazz._log.log_d(f'{label}: 3: file_mtime={file_mtime}')
    clazz.set_date(filename, mtime_key, file_mtime)
    # setting the date in the line above has the side effect
    # of changing the mtime in some implementations.  so we
    # force it to be what it was right after setting the value
    # which is in the past (usually microseconds) but guaranteed
    # to match what what was set in set_date()
    #bfile_date.set_modification_date(filename, file_mtime)
    return clazz._get_cached_bytes_result(value, file_mtime, mtime_key, False)

  @classmethod
  def remove_mtime_key(clazz, filename, key):
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    mtime_key = clazz._make_mtime_key(key)

    if clazz.has_key(filename, mtime_key):
      clazz.remove(filename, mtime_key)
