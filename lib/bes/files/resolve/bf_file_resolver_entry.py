#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from ..bf_entry import bf_entry

class bf_file_resolver_entry(bf_entry):

  _log = logger('resolve')
  
  def __init__(self, filename, root_dir = None, index = None, found_index = None):
    super().__init__(filename, root_dir = root_dir)

    self._index = index
    self._found_index = found_index

  @property
  def index(self):
    return self._index

  @index.setter
  def index(self, index):
    self._index = index
