#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.property.cached_property import cached_property
from bes.system.check import check
from bes.system.log import logger

from ..attributes.bfile_attr_file import bfile_attr_file

from .bfile_metadata_file import bfile_metadata_file

class bfile_metadata_poto(object):

  _log = logger('bfile_metadata_poto')

  def __init__(self, filename):
    self._metadata = bfile_metadata_file(filename)

  @property
  def filename(self):
    return self._metadata.filename
  
  def __getitem__(self, key):
    return self._metadata.get_metadata(key)

  def __setitem__(self, key, value):
    print(f'__setitem__: key={key} value={value}')
    return 666
  
#  def get_metadata(self, key):
#    key = check.check_bfile_metadata_key(key)
#    return bfile_metadata.get_metadata(self._filename, key)

#  def get_metadata_getter_count(self, key):
#    key = check.check_bfile_metadata_key(key)
#    return bfile_metadata.get_metadata_getter_count(self._filename, key)
