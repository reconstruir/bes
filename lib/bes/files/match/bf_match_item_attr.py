#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from .bf_match_item_base import bf_match_item_base
from .bf_match_options import bf_match_options

class bf_match_item_attr(bf_match_item_base):

  def __init__(self, attrs):
    check.check_dict(attrs)

    self._attrs = attrs

  #@abstractmethod
  def match(self, entry, options):
    'Return True if entry matches.'
    check.check_bfile_entry(entry)
    check.check_bf_match_options(options)

    for key, value in self._attrs.items():
      if not key in entry.attributes:
        return False
      if entry.attributes[key] != value:
        return False
    return True
