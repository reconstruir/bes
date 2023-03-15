#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

from bes.system.check import check

from ..bfile_entry import bfile_entry

from .bfile_matcher_match_type import bfile_matcher_match_type

class bfile_matcher_base(with_metaclass(ABCMeta, object)):

  @abstractmethod
  def match(self, entry, options):
    'Return True if entry matches.'
    raise NotImplemented('match')

  def _match_sequence(self, entry, items, match_type, match_function, options):
    check.check_bfile_entry(entry)
    check.check_callable(match_function)

    func_map = {
      bfile_matcher_match_type.ALL: self._match_all,
      bfile_matcher_match_type.ANY: self._match_any,
      bfile_matcher_match_type.NONE: self._match_none,
    }
    func = func_map[match_type]
    return func(match_function, entry, items, options)

  @staticmethod
  def _match_any(match_function, entry, items, options):
    for next_item in items:
      if match_function(entry, next_item, options):
        return True
    return False

  @staticmethod
  def _match_all(match_function, entry, items, options):
    for next_item in items:
      if not match_function(entry, next_item, options):
        return False
    return True

  @staticmethod
  def _match_none(match_function, entry, items, options):
    for next_item in items:
      if match_function(entry, next_item, options):
        return False
    return True

  @classmethod
  def check_sequence(clazz, seq):
    if check.is_string_seq(seq):
      return [ i for i in seq ]
    elif check.is_string(seq):
      return [ seq ]
    raise TypeError(f'seq should be a string or string sequence: "{seq}" - {type(seq)}')

check.register_class(bfile_matcher_base, name = 'bfile_matcher', include_seq = False)
