#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.bcli.bcli_type_i import bcli_type_i

from bes.system.check import check
from bes.system.log import logger
from bes.common.object_util import object_util

from ..bf_entry import bf_entry
from ..bf_entry_list import bf_entry_list

from .bf_file_matcher_item_attr import bf_file_matcher_item_attr
from .bf_file_matcher_item_i import bf_file_matcher_item_i
from .bf_file_matcher_item_callable import bf_file_matcher_item_callable
from .bf_file_matcher_item_datetime import bf_file_matcher_item_datetime
from .bf_file_matcher_item_fnmatch import bf_file_matcher_item_fnmatch
from .bf_file_matcher_item_fnmatch_list import bf_file_matcher_item_fnmatch_list
from .bf_file_matcher_type import bf_file_matcher_type
from .bf_file_matcher_item_metadata import bf_file_matcher_item_metadata
from .bf_file_matcher_options import bf_file_matcher_options
from .bf_file_matcher_item_re import bf_file_matcher_item_re
from .bf_file_matcher_item_timedelta import bf_file_matcher_item_timedelta

class bf_file_matcher(object):

  _log = logger('bf_file_matcher')
  
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

  def clone(self):
    result = bf_file_matcher()
    for matcher_item in self._matchers:
      result.add_matcher(matcher_item.matcher.clone(), matcher_item.negate)
    return result
      
  @property
  def empty(self):
    return len(self._matchers) == 0

  _matcher_item = namedtuple('_matcher_item', 'matcher, negate')
  def add_matcher(self, matcher, negate = False):
    check.check_bf_file_matcher_item(matcher)
    check.check_bool(negate)

    self._matchers.append(self._matcher_item(matcher, negate))

  def add_matcher_fnmatch(self, pattern, negate = False):
    self.add_matcher(bf_file_matcher_item_fnmatch(pattern), negate = negate)

  def add_matcher_fnmatch_list(self, patterns, match_type = bf_file_matcher_type.ANY):
    self.add_matcher(bf_file_matcher_item_fnmatch_list(patterns, match_type))
    
  def add_matcher_re(self, expression, negate = False):
    self.add_matcher(bf_file_matcher_item_re(expression), negate = negate)

  def add_matcher_callable(self, callable_, negate = False):
    self.add_matcher(bf_file_matcher_item_callable(callable_), negate = negate)

  def add_matcher_datetime(self, date, comparison_type, negate = False):
    self.add_matcher(bf_file_matcher_item_datetime(date, comparison_type), negate = negate)

  def add_matcher_timedelta(self, delta, comparison_type, negate = False):
    self.add_matcher(bf_file_matcher_item_timedelta(delta, comparison_type), negate = negate)

  def add_matcher_attr(self, attrs, negate = False):
    self.add_matcher(bf_file_matcher_item_attr(attrs), negate = negate)

  def add_matcher_metadata(self, metadatas, negate = False):
    self.add_matcher(bf_file_matcher_item_metadata(metadatas), negate = negate)
    
  def match(self, entry, options = None):
    check.check_bf_entry(entry)
    options = check.check_bf_file_matcher_options(options, allow_none = True) or bf_file_matcher_options()

    self._log.log_d(f'match: entry={entry.filename} options={options}')
    
    if self.empty:
      self._log.log_d(f'match: no matchers found')
      return True
    
    func_map = {
      bf_file_matcher_type.ALL: self._match_all,
      bf_file_matcher_type.ANY: self._match_any,
      bf_file_matcher_type.NONE: self._match_none,
    }
    func = func_map[options.match_type]
    return func(entry, self._matchers, options)

  def match_entries(self, entries, options = None):
    entries = check.check_bf_entry_list(entries)
    options = check.check_bf_file_matcher_options(options, allow_none = True) or bf_file_matcher_options()

    if self.empty:
      return entries[:]

    result = bf_entry_list()
    for entry in entries:
      match_result = self.match(entry, options = options)
      if match_result:
        result.append(entry)
    return result
  
  @classmethod
  def _match_any(clazz, entry, matchers, options):
    num = len(matchers)
    for i, next_matcher in enumerate(matchers, start = 1):
      matched = next_matcher.matcher.match(entry, options)
      if next_matcher.negate:
        matched = not matched
      clazz._log.log_d(f'_match_any: {i} of {num}: entry={entry.filename} matcher={next_matcher.matcher} => {matched}')
      if matched:
        return True
    return False

  @classmethod
  def _match_all(clazz, entry, matchers, options):
    num = len(matchers)
    for i, next_matcher in enumerate(matchers, start = 1):
      matched = next_matcher.matcher.match(entry, options)
      if next_matcher.negate:
        matched = not matched
      clazz._log.log_d(f'_match_all: {i} of {num}:  entry={entry.filename} matcher={next_matcher.matcher} => {matched}')
      if not matched:
        return False
    return True

  @classmethod
  def _match_none(clazz, entry, matchers, options):
    num = len(matchers)
    for i, next_matcher in enumerate(matchers, start = 1):
      matched = next_matcher.matcher.match(entry, options)
      if next_matcher.negate:
        matched = not matched
      clazz._log.log_d(f'_match_none: {i} of {num}:  entry={entry.filename} matcher={next_matcher.matcher} => {matched}')
      if matched:
        return False
    return True
      
check.register_class(bf_file_matcher, include_seq = False)

class bf_cli_match(bcli_type_i):

  @classmethod
  #@abstractmethod
  def name_str(clazz):
    return 'bf_file_matcher'

  @classmethod
  #@abstractmethod
  def type_function(clazz):
    return bf_file_matcher

  @classmethod
  #@abstractmethod
  def parse(clazz, text):
    assert False
    return text

  @classmethod
  #@abstractmethod
  def check(clazz, value, allow_none = False):
    return check.check_bf_file_matcher(value, allow_none = allow_none)
