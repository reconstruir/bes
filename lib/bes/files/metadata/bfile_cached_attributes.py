#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path
import os
#
#from bes.common.bool_util import bool_util
#from bes.common.hash_util import hash_util
#from bes.common.time_util import time_util
#from bes.fs.file_check import file_check
#from bes.property.cached_property import cached_property
from bes.system.check import check
from bes.system.log import logger
from bes.fs.file_check import file_check
#
#from .file_attributes import file_attributes
#from .file_attributes_error import file_attributes_permission_error
#from .file_mime import file_mime
#from .file_path import file_path
#from .file_util import file_util
#
#from .file_metadata_getter_base import file_metadata_getter_base
#from .file_metadata_getter_checksum_md5 import file_metadata_getter_checksum_md5
#from .file_metadata_getter_checksum_sha1 import file_metadata_getter_checksum_sha1
#from .file_metadata_getter_checksum_sha256 import file_metadata_getter_checksum_sha256
#from .file_metadata_getter_media_type import file_metadata_getter_media_type
#from .file_metadata_getter_mime_type import file_metadata_getter_mime_type

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
