#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from ..bf_entry import bf_entry

class bf_file_resolver_entry(bf_entry):

  _log = logger('resolve')
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self._index = None
    self._found_index = None

  def to_dict(self, replacements = None, xp_filenames = False):
    d = super().to_dict(replacements = replacements, xp_filenames = xp_filenames)
    d.update( {
      'index': self.index,
      'found_index': self.found_index,
    })
    return d
    
  @property
  def index(self):
    return self._index

  @index.setter
  def index(self, index):
    self._index = index

  @property
  def found_index(self):
    return self._found_index

  @found_index.setter
  def found_index(self, found_index):
    self._found_index = found_index
    
