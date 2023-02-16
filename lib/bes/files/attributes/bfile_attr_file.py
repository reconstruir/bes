#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from .bfile_attr import bfile_attr

class bfile_attr_file(object):

  _log = logger('bfile_attr_file')
  
  def __init__(self, filename):
    self._filename = filename

  @property
  def filename(self):
    return self._filename

  def has_key(self, key):
    bfile_attr.check_key(key)

    return bfile_attr.has_key(self._filename, key)

  def get_bytes(self, key):
    bfile_attr.check_key(key)

    return bfile_attr.get_bytes(self._filename, key)

  def set_bytes(self, key, value):
    bfile_attr.check_key(key)
    check.check_bytes(value)

    bfile_attr.set_bytes(self._filename, key, value)

  def remove(self, key):
    bfile_attr.check_key(key)

    bfile_attr.remove(self._filename, key)

  def keys(self):
    return bfile_attr.keys(self._filename)

  def clear(self):
    bfile_attr.clear(self._filename)

  def get_all(self):
    return bfile_attr.get_all(self._filename)

  def set_all(self, attributes):
    bfile_attr.set_all(self._filename, attributes)

  def get_string(self, key):
    bfile_attr.check_key(key)
    
    return bfile_attr.get_string(self._filename, key)

  def set_string(self, key, value):
    bfile_attr.check_key(key)

    bfile_attr.set_string(self._filename, key, value)

  def get_date(self, key):
    bfile_attr.check_key(key)

    return bfile_attr.get_date(self._filename, key)

  def set_date(self, key, value):
    bfile_attr.check_key(key)

    bfile_attr.set_date(self._filename, key, value)

  def get_bool(self, key):
    bfile_attr.check_key(key)

    return bfile_attr.get_bool(self._filename, key)

  def set_bool(self, key, value):
    bfile_attr.check_key(key)

    bfile_attr.set_bool(self._filename, key, value)
    
  def get_int(self, key):
    bfile_attr.check_key(key)

    return bfile_attr.get_int(self._filename, key)

  def set_int(self, key, value):
    bfile_attr.check_key(key)

    bfile_attr.set_int(self._filename, key, value)
