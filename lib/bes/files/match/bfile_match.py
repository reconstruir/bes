#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from ..bfile_entry import bfile_entry
from ..bfile_entry_list import bfile_entry_list

from .bfile_matcher_base import bfile_matcher_base
from .bfile_matcher_callable import bfile_matcher_callable
from .bfile_matcher_fnmatch import bfile_matcher_fnmatch
from .bfile_matcher_match_type import bfile_matcher_match_type
from .bfile_matcher_options import bfile_matcher_options
from .bfile_matcher_re import bfile_matcher_re

class bfile_match(object):

  _log = logger('bfile_match')
  
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

    self._log.log_d(f'match: entry={entry.filename} options={options}')
    
    if not self._matchers:
      self._log.log_d(f'match: no matchers found')
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
  
  @classmethod
  def _match_any(clazz, entry, matchers, options):
    num = len(matchers)
    for i, next_matcher in enumerate(matchers, start = 1):
      matched = next_matcher.match(entry, options)
      clazz._log.log_d(f'_match_any: {i} of {num}: entry={entry.filename} matcher={next_matcher} => {matched}')
      if matched:
        return True
    return False

  @classmethod
  def _match_all(clazz, entry, matchers, options):
    num = len(matchers)
    for i, next_matcher in enumerate(matchers, start = 1):
      matched = next_matcher.match(entry, options)
      clazz._log.log_d(f'_match_all: {i} of {num}:  entry={entry.filename} matcher={next_matcher} => {matched}')
      if not matched:
        return False
    return True

  @classmethod
  def _match_none(clazz, entry, matchers, options):
    num = len(matchers)
    for i, next_matcher in enumerate(matchers, start = 1):
      matched = next_matcher.match(entry, options)
      clazz._log.log_d(f'_match_none: {i} of {num}:  entry={entry.filename} matcher={next_matcher} => {matched}')
      if matched:
        return False
    return True
      
check.register_class(bfile_match, include_seq = False)
