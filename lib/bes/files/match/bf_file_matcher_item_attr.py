#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy

from bes.system.check import check

from .bf_file_matcher_item_i import bf_file_matcher_item_i
from .bf_file_matcher_options import bf_file_matcher_options

class bf_file_matcher_item_attr(bf_file_matcher_item_i):

  def __init__(self, attrs):
    check.check_dict(attrs)

    self._attrs = attrs

  #@abstractmethod
  def match(self, entry, options):
    'Return True if entry matches.'
    check.check_bf_entry(entry)
    check.check_bf_file_matcher_options(options)

    for key, value in self._attrs.items():
      if not key in entry.attributes:
        return False
      if entry.attributes[key] != value:
        return False
    return True

  #@abstractmethod
  def clone(self):
    'Clone the matcher item.'
    raise bf_file_matcher_item_attr(copy.deepcopy(self._attrs))
