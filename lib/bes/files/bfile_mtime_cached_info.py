#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.system.check import check
from bes.system.log import logger

class bfile_mtime_cached_info(object):

  _log = logger('bfile_mtime_cached_info')
  
  def __init__(self, filename, info_getter):
    check.check_callable(info_getter)

    self._filename = filename
    self._info_getter = info_getter
    self._value = None
    self._last_mtime = None
    self._count = 0

  @property
  def value(self):
    current_mtime = path.getmtime(self._filename)
    if self._last_mtime != None:
      assert not self._last_mtime > current_mtime
      if current_mtime <= self._last_mtime:
        assert self._value != None
        return self._value
    self._last_mtime = current_mtime
    self._value = self._info_getter(self._filename)
    self._count += 1
    assert self._value != None
    return self._value

  @property
  def count(self):
    return self._count
  
check.register_class(bfile_mtime_cached_info, include_seq = False)
