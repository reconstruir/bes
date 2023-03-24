#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger
from bes.common.object_util import object_util

from ..bf_entry import bf_entry
from ..bf_entry_list import bf_entry_list

from .bf_match_item_attr import bf_match_item_attr
from .bf_match_item_base import bf_match_item_base
from .bf_match_item_callable import bf_match_item_callable
from .bf_match_item_datetime import bf_match_item_datetime
from .bf_match_item_fnmatch import bf_match_item_fnmatch
from .bf_match_type import bf_match_type
from .bf_match_item_metadata import bf_match_item_metadata
from .bf_match_options import bf_match_options
from .bf_match_item_re import bf_match_item_re
from .bf_match_item_timedelta import bf_match_item_timedelta

class bf_match(object):

  _log = logger('match')
  
  def __init__(self, patterns = None, expressions = None, callables = None,
               attrs = None, metadatas = None):
    patterns = check.check_string_seq(patterns, allow_none = True, default_value = [])
    expressions = check.check_string_seq(expressions, allow_none = True, default_value = [])
    callables = check.check_callable_seq(callables, allow_none = True, default_value = [])
    check.check_dict(attrs, allow_none = True)
    check.check_dict(metadatas, allow_none = True)
    
    self._matchers = []
    for pattern in patterns:
      self.add_matcher_fnmatch(pattern)
    for expression in expressions:
      self.add_matcher_re(expression)
    for callable_ in callables:
      self.add_matcher_callable(callable_)
    if attrs:
      self.add_matcher_attr(attrs)
    if metadatas:
      self.add_matcher_metadata(metadatas)

  @property
  def empty(self):
    return len(self._matchers) == 0
    
  def add_matcher(self, matcher):
    check.check_bf_matcher(matcher)

    self._matchers.append(matcher)

  def add_matcher_fnmatch(self, pattern):
    self.add_matcher(bf_match_item_fnmatch(pattern))

  def add_matcher_re(self, expression):
    self.add_matcher(bf_match_item_re(expression))

  def add_matcher_callable(self, callable_):
    self.add_matcher(bf_match_item_callable(callable_))

  def add_matcher_datetime(self, date, comparison_type):
    self.add_matcher(bf_match_item_datetime(date, comparison_type))

  def add_matcher_timedelta(self, delta, comparison_type):
    self.add_matcher(bf_match_item_timedelta(delta, comparison_type))

  def add_matcher_attr(self, attrs):
    self.add_matcher(bf_match_item_attr(attrs))

  def add_matcher_metadata(self, metadatas):
    self.add_matcher(bf_match_item_metadata(metadatas))
    
  def match(self, entry, options = None):
    check.check_bf_entry(entry)
    options = check.check_bf_match_options(options, allow_none = True) or bf_match_options()

    self._log.log_d(f'match: entry={entry.filename} options={options}')
    
    if self.empty:
      self._log.log_d(f'match: no matchers found')
      return True
    
    func_map = {
      bf_match_type.ALL: self._match_all,
      bf_match_type.ANY: self._match_any,
      bf_match_type.NONE: self._match_none,
    }
    func = func_map[options.match_type]
    return func(entry, self._matchers, options)

  def match_entries(self, entries, options = None):
    entries = check.check_bf_entry_list(entries)
    options = check.check_bf_match_options(options, allow_none = True) or bf_match_options()

    if self.empty:
      return entries[:]

    result = bf_entry_list()
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
      
check.register_class(bf_match, include_seq = False)
