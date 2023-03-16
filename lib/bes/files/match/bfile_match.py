#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from ..bfile_entry import bfile_entry
from ..bfile_entry_list import bfile_entry_list

from .bfile_matcher_match_type import bfile_matcher_match_type
from .bfile_matcher_options import bfile_matcher_options
from .bfile_matcher_base import bfile_matcher_base
from .bfile_matcher_fnmatch import bfile_matcher_fnmatch
from .bfile_matcher_re import bfile_matcher_re
from .bfile_matcher_callable import bfile_matcher_callable

class bfile_match(object):

  def __init__(self):
    self._matchers = []
    
  def add_matcher(self, matcher):
    check.check_bfile_matcher(matcher)

    self._matchers.append(matcher)

  def add_matcher_fnmatch(self, pattern):
    self.add_matcher(bfile_matcher_fnmatch(pattern))

  def add_matcher_re(self, expression):
    self.add_matcher(bfile_matcher_re(expression))

  def add_matcher_callable(self, callable_, **options):
    self.add_matcher(bfile_matcher_callable(callable_))
    
  def match(self, entry, options = None):
    check.check_bfile_entry(entry)
    options = check.check_bfile_matcher_options(options, allow_none = True) or bfile_matcher_options()

    if not self._matchers:
      return True
    
    func_map = {
      bfile_matcher_match_type.ALL: self._match_all,
      bfile_matcher_match_type.ANY: self._match_any,
      bfile_matcher_match_type.NONE: self._match_none,
    }
    func = func_map[options.match_type]
    return func(entry, self._matchers, options)

  def match_entries(self, entries, options = None):
    entries = check.check_bfile_entry_list(entries)
    options = check.check_bfile_matcher_options(options, allow_none = True) or bfile_matcher_options()

    if not self._matchers:
      return entries[:]

    result = bfile_entry_list()
    for entry in entries:
      if self.match(entry, options = options):
        result.append(entry)
    return result
  
  @staticmethod
  def _match_any(entry, matchers, options):
    for next_matcher in matchers:
      if next_matcher.match(entry, options):
        return True
    return False

  @staticmethod
  def _match_all(entry, matchers, options):
    for next_matcher in matchers:
      if not next_matcher.match(entry, options):
        return False
    return True

  @staticmethod
  def _match_none(entry, matchers, options):
    for next_matcher in matchers:
      if next_matcher.match(entry, options):
        return True
    return False
      
check.register_class(bfile_match, include_seq = False)
