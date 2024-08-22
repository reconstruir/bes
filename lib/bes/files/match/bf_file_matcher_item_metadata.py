#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy

from bes.system.check import check

from .bf_file_matcher_item_i import bf_file_matcher_item_i
from .bf_file_matcher_options import bf_file_matcher_options

class bf_file_matcher_item_metadata(bf_file_matcher_item_i):

  def __init__(self, metadatas):
    check.check_dict(metadatas)

    self._metadatas = metadatas

  #@abstractmethod
  def match(self, entry, options):
    'Return True if entry matches.'
    check.check_bf_entry(entry)
    check.check_bf_file_matcher_options(options)

    for key, value in self._metadatas.items():
      if not entry.metadata[key] == value:
        return False
    return True

  #@abstractmethod
  def clone(self):
    'Clone the matcher item.'
    raise bf_file_matcher_item_metadata(copy.deepcopy(self._metadatas))
  
