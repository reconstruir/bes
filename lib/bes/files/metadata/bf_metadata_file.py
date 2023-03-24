#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.property.cached_property import cached_property
from bes.system.check import check
from bes.system.log import logger

from ..attr.bf_attr_file import bf_attr_file

from .bf_metadata import bf_metadata
from .bf_metadata_error import bf_metadata_error
from .bf_metadata_key_error import bf_metadata_key_error

class bf_metadata_file(bf_attr_file):

  _log = logger('metadata')

  def get_metadata(self, key):
    key = check.check_bf_metadata_key(key)
    return bf_metadata.get_metadata(self._filename, key)

  def get_metadata_getter_count(self, key):
    key = check.check_bf_metadata_key(key)
    return bf_metadata.get_metadata_getter_count(self._filename, key)

  def has_metadata(self, key):
    key = check.check_bf_metadata_key(key)

    return bf_metadata.has_metadata(self._filename, key)

  def metadata_delete(self, key):
    key = check.check_bf_metadata_key(key)

    return bf_metadata.metadata_delete(self._filename, key)

  def __delitem__(self, key):
    if not self.has_metadata(key):
      raise bf_metadata_key_error(f'No key "{key}" found for "{self.filename}"')
    self.metadata_delete(key)
  
  def __contains__(self, key):
    return self.has_metadata(key)
  
  def __getitem__(self, key):
    try:
      return self.get_metadata(key)
    except bf_metadata_error as ex:
      raise bf_metadata_key_error(f'No key "{key}" found for "{self.filename}"')

  def __setitem__(self, key, value):
    raise bf_metadata_error(f'metadata "{key}" is read-only.')
