#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path
from collections import namedtuple

from bes.common.hash_util import hash_util
from bes.common.time_util import time_util
from bes.property.cached_property import cached_property
from bes.system.check import check
from bes.system.log import logger

from .bfile_date import bfile_date
from .bfile_error import bfile_error
from .bfile_filename import bfile_filename
from .bfile_mtime_cached_info import bfile_mtime_cached_info
from .bfile_permission_error import bfile_permission_error

from .attributes.bfile_attr import bfile_attr
from .metadata.bfile_metadata import bfile_metadata

class bfile_entry(object):

  _log = logger('bfile_entry')
  
  def __init__(self, filename):
    self._filename = filename
    self._stat = bfile_mtime_cached_info(self._filename, lambda f: os.stat(filename, follow_symlinks = True))

  @cached_property
  def filename(self):
    return self._filename

  @cached_property
  def filename_lowercase(self):
    return self.filename.lower()
  
  @cached_property
  def dirname(self):
    return path.dirname(self._filename)

  @cached_property
  def dirname_lowercase(self):
    return self.dirname.lower()
  
  @cached_property
  def basename(self):
    return path.basename(self._filename)

  @cached_property
  def extension(self):
    return bfile_filename.extension(self._filename)

  @cached_property
  def extension_lowercase(self):
    return self.extension.lower()
  
  @property
  def exists(self):
    return  path.exists(self._filename)

  @property
  def is_readable(self):
    return os.access(self._filename, os.R_OK)

  @property
  def is_writable(self):
    return os.access(self._filename, os.W_OK)

  @property
  def is_executable(self):
    return os.access(self._filename, os.F_OK)
  
  _access_result = namedtuple('_access_result', 'exists, can_read, can_write, can_execute')
  @property
  def access(self):
    exists = os.access(self._filename, os.F_OK)
    if exists:
      can_read = os.access(self._filename, os.R_OK)
      can_write = os.access(self._filename, os.W_OK)
      can_execute = os.access(self._filename, os.X_OK)
    else:
      can_read = False
      can_write = False
      can_execute = False
    return self._access_result(exists, can_read, can_write, can_execute)
  
  @property
  def stat(self):
    return self._stat.value

  @cached_property
  def hashed_filename_sha256(self):
    return hash_util.hash_string_sha256(self._filename)
  
  @cached_property
  def basename_lowercase(self):
    return self.basename.lower()

  @property
  def is_dir(self):
    return path.isdir(self._filename)
  
  @property
  def is_file(self):
    return path.isfile(self._filename)
  
  @property
  def size(self):
    return self.stat.st_size
  
  @property
  def modification_date(self):
    return bfile_date.get_modification_date(self._filename)

  @modification_date.setter
  def modification_date(self, mtime):
    check.check_datetime(mtime)

    bfile_date.set_modification_date(self._filename, mtime)

  @property
  def modification_date_timestamp(self):
    return time_util.timestamp(when = self.modification_date, milliseconds = False)

  def attr_has_key(self, key):
    check.check_string(key)

    return bfile_attr.has_key(self._filename, key)

  def attr_get_bytes(self, key):
    check.check_string(key)

    return bfile_attr.get_bytes(self._filename, key)

  def attr_set_bytes(self, key, value):
    check.check_string(key)
    check.check_bytes(value)

    bfile_attr.set_bytes(self._filename, key, value)

  def attr_remove(self, key):
    check.check_string(key)

    bfile_attr.remove(self._filename, key)

  def attr_keys(self):
    return bfile_attr.keys(self._filename)

  def attr_clear(self):
    bfile_attr.clear(self._filename)

  def attr_get_all(self):
    return bfile_attr.get_all(self._filename)

  def attr_set_all(self, attributes):
    bfile_attr.set_all(self._filename, attributes)

  def attr_get_string(self, key):
    return bfile_attr.get_string(self._filename, key)

  def attr_set_string(self, key, value):
    bfile_attr.set_string(self._filename, key, value)

  def attr_get_date(self, key):
    return bfile_attr.get_date(self._filename, key)

  def attr_set_date(self, key, value):
    bfile_attr.set_date(self._filename, key, value)

  def attr_get_bool(self, key):
    return bfile_attr.get_bool(self._filename, key)

  def attr_set_bool(self, key, value):
    bfile_attr.set_bool(self._filename, key, value)
    
  def attr_get_int(self, key):
    return bfile_attr.get_int(self._filename, key)

  def attr_set_int(self, key, value):
    bfile_attr.set_int(self._filename, key, value)

    
check.register_class(bfile_entry, include_seq = False)
