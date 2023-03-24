#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from .bf_match_item_base import bf_match_item_base
from .bf_match_options import bf_match_options

class bf_match_item_metadata(bf_match_item_base):

  def __init__(self, metadatas):
    check.check_dict(metadatas)

    self._metadatas = metadatas

  #@abstractmethod
  def match(self, entry, options):
    'Return True if entry matches.'
    check.check_bf_entry(entry)
    check.check_bf_match_options(options)

    for key, value in self._metadatas.items():
      if not entry.metadata[key] == value:
        return False
    return True
