#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path
import os

from bes.system.check import check
from bes.system.log import logger

from ..bfile_permission_error import bfile_permission_error
from ..bfile_error import bfile_error

class bfile_cached_attributes(object):

  _log = logger('bfile_cached_attributes')
  
  def __init__(self, filename):
    self._filename = filename
    self._values = {}

  _value_makers = {}
  @classmethod
  def register_value_maker(clazz, key, value_maker):
    check.check_string(key)
    check.check_callable(value_maker)

    if key in clazz._value_makers:
      raise bfile_error(f'value maker for "{key}" already registered')
    clazz._value_makers[key] = value_maker
    
  @property
  def mtime(self):
    return path.getmtime(self._filename)

  _value_item = namedtuple('_value_item', 'value, mtime')
  def get_value(self, key):
    check.check_string(key)

    self._log.log_method_d()

    if not os.access(self._filename, os.R_OK):
      raise bfile_permission_error(f'No read access: {filename}')

    value_maker = self._value_makers.get(key, None)
    if not value_maker:
      raise bfile_error(f'no value maker registered for "{key}"')
    
    item = self._values.get(key, None)
    if item:
      if self.mtime > item.mtime:
        item = None
    if not item:
      value = value_maker(self._filename)
      item = self._value_item(value, self.mtime)
      self._values[key] = item
    return item.value

  @classmethod
  def register_common_value_makers(clazz):
    clazz.register_value_maker('stat', lambda filename: os.stat(filename, follow_symlinks = True))

bfile_cached_attributes.register_common_value_makers()

check.register_class(bfile_cached_attributes, include_seq = False)
