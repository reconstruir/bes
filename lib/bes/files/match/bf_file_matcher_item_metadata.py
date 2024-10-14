#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy

from bes.system.check import check

from .bf_file_matcher_item_base import bf_file_matcher_item_base

class bf_file_matcher_item_metadata(bf_file_matcher_item_base):

  def __init__(self, metadatas, file_type = None):
    super().__init__(file_type, None)
    self._metadatas = check.check_dict(metadatas)

  def __str__(self):
    return f'fmi_metadata("{[ key for key in self._metadatas.keys()]}")'
    
  #@abstractmethod
  def match(self, entry):
    'Return True if entry matches.'
    check.check_bf_entry(entry)

    matched_type = self.match_file_type(entry)
    matched = False
    if matched_type:
      matched = True
      for key, value in self._metadatas.items():
        if not entry.metadata[key] == value:
          matched = False
          break
    return matched

  #@abstractmethod
  def clone(self):
    'Clone the matcher item.'
    return bf_file_matcher_item_metadata(copy.deepcopy(self._metadatas), self.file_type)
