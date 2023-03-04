#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from .bfile_matcher_base import bfile_matcher_base
from .bfile_filename_match_type import bfile_filename_match_type

from ..bfile_entry import bfile_entry

class bfile_matcher_sequence(bfile_matcher_base):
    
  def _match_sequence(self, entry, items, match_type, match_function):
    check.check_bfile_entry(entry)
    check.check_callable(match_function)

    func_map = {
      bfile_filename_match_type.ALL: self._match_all,
      bfile_filename_match_type.ANY: self._match_any,
      bfile_filename_match_type.NONE: self._match_none,
    }
    func = func_map[match_type]
    return func(match_function, entry, items)

  @staticmethod
  def _match_any(match_function, entry, items):
    for next_item in items:
      if match_function(entry, next_item):
        return True
    return False

  @staticmethod
  def _match_all(match_function, entry, items):
    for next_item in items:
      if not match_function(entry, next_item):
        return False
    return True

  @staticmethod
  def _match_none(match_function, entry, items):
    for next_item in items:
      if match_function(entry, next_item):
        return False
    return True
  
