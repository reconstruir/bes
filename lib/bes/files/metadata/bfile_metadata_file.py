#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.property.cached_property import cached_property
from bes.system.check import check
from bes.system.log import logger

from ..attributes.bfile_attr_file import bfile_attr_file

from .bfile_metadata import bfile_metadata

class bfile_metadata_file(bfile_attr_file):

  _log = logger('bfile_metadata_file')

  def get_metadata(self, key):
    key = check.check_bfile_metadata_key(key)
    return bfile_metadata.get_metadata(self._filename, key)

  def set_metadata(self, key, value):
    key = check.check_bfile_metadata_key(key)
    return bfile_metadata.set_metadata(self._filename, key, value)
  
  def get_metadata_getter_count(self, key):
    key = check.check_bfile_metadata_key(key)
    return bfile_metadata.get_metadata_getter_count(self._filename, key)
