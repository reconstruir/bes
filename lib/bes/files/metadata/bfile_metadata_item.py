#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.property.cached_property import cached_property
from bes.system.check import check
from bes.system.log import logger

from .bfile_metadata_file import bfile_metadata_file
from .bfile_metadata_error import bfile_metadata_error
from .bfile_metadata_key_error import bfile_metadata_key_error

class bfile_metadata_item(object):

  _log = logger('metadata')

  def __init__(self, filename):
    self._metadata = bfile_metadata_file(filename)

  @property
  def filename(self):
    return self._metadata.filename

  def __delitem__(self, key):
    if not self._metadata.has_metadata(key):
      raise bfile_metadata_key_error(f'No key "{key}" found for "{self.filename}"')
    self._metadata.metadata_delete(key)
  
  def __contains__(self, key):
    return self._metadata.has_metadata(key)
  
  def __getitem__(self, key):
    try:
      return self._metadata.get_metadata(key)
    except bfile_metadata_error as ex:
      raise bfile_metadata_key_error(f'No key "{key}" found for "{self.filename}"')

  def __setitem__(self, key, value):
    self._metadata.set_metadata(key, value)
