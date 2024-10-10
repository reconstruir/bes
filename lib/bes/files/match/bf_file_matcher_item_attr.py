#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy

from bes.system.check import check

from .bf_file_matcher_item_base import bf_file_matcher_item_base

class bf_file_matcher_item_attr(bf_file_matcher_item_base):

  def __init__(self, attrs, file_type = None):
    super().__init__(file_type, None)
    self._attrs = check.check_dict(attrs)

  #@abstractmethod
  def match(self, entry):
    'Return True if entry matches.'
    check.check_bf_entry(entry)

    matched_type = self.match_file_type(entry)
    matched = False
    if matched_type:
      matched = True
      for key, value in self._attrs.items():
        if not key in entry.attributes:
          matched = False
          break
        if entry.attributes[key] != value:
          matched = False
          break
    return matched

  #@abstractmethod
  def clone(self):
    'Clone the matcher item.'
    return bf_file_matcher_item_attr(copy.deepcopy(self._attrs), self.file_type)
