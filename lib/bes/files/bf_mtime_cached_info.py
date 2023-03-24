#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.system.check import check
from bes.system.log import logger

from .bf_date import bf_date

class bf_mtime_cached_info(object):

  _log = logger('bf_mtime_cached_info')
  
  def __init__(self, filename, info_getter):
    check.check_callable(info_getter)

    self._filename = filename
    self._info_getter = info_getter
    self._value = None
    self._last_mtime = None
    self._count = 0

  @property
  def value(self):
    current_mtime = bf_date.get_modification_date(self._filename)
    self._log.log_d(f'value: current_mtime={current_mtime} last_mtime={self._last_mtime}')
    if self._last_mtime != None:
      assert not self._last_mtime > current_mtime
      if current_mtime <= self._last_mtime:
        assert self._value != None
        return self._value
    self._last_mtime = current_mtime
    self._value = self._info_getter(self._filename)
    self._count += 1
    assert self._value != None
    self._log.log_d(f'value: value={self._value} count={self._count}')
    return self._value

  @property
  def count(self):
    return self._count
  
check.register_class(bf_mtime_cached_info, include_seq = False)
