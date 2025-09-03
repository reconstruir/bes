#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.bcli.bcli_type_i import bcli_type_i

from bes.system.check import check
from bes.system.log import logger
from bes.common.object_util import object_util

from ..bf_entry import bf_entry
from ..bf_entry_list import bf_entry_list
from ..bf_file_type import bf_file_type
from ..bf_path_type import bf_path_type

from .bf_file_matcher_item_attr import bf_file_matcher_item_attr
from .bf_file_matcher_item_callable import bf_file_matcher_item_callable
from .bf_file_matcher_item_datetime import bf_file_matcher_item_datetime
from .bf_file_matcher_item_fnmatch import bf_file_matcher_item_fnmatch
from .bf_file_matcher_item_fnmatch_list import bf_file_matcher_item_fnmatch_list
from .bf_file_matcher_item_i import bf_file_matcher_item_i
from .bf_file_matcher_item_metadata import bf_file_matcher_item_metadata
from .bf_file_matcher_item_re import bf_file_matcher_item_re
from .bf_file_matcher_mode import bf_file_matcher_mode

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
      self.add_item_fnmatch(pattern)
    for expression in expressions:
      self.add_item_re(expression)
    for callable_ in callables:
      self.add_item_callable(callable_)
    if attrs:
      self.add_item_attr(attrs)
    if metadatas:
      self.add_item_metadata(metadatas)

  def clone(self):
    result = bf_file_matcher()
    for matcher_item in self._matchers:
      result.add_item(matcher_item.matcher.clone(), matcher_item.negate)
    return result
      
  @property
  def empty(self):
    return len(self._matchers) == 0

  _matcher_item = namedtuple('_matcher_item', 'matcher, negate')
  def add_item(self, matcher, negate = False):
    check.check_bf_file_matcher_item(matcher)
    check.check_bool(negate)

    self._matchers.append(self._matcher_item(matcher, negate))
    
  def add_item_fnmatch(self,
                       pattern,
                       file_type = None,
                       path_type = None,
                       ignore_case = False,
                       negate = False):
    item = bf_file_matcher_item_fnmatch(pattern,
                                        file_type = file_type,
                                        path_type = path_type,
                                        ignore_case = ignore_case)
    self.add_item(item, negate = negate)

  def add_item_fnmatch_list(self,
                            patterns,
                            list_match_type = bf_file_matcher_mode.ANY,
                            file_type = None,
                            path_type = None,
                            ignore_case = False,
                            negate = False):
    item = bf_file_matcher_item_fnmatch_list(patterns,
                                             list_match_type,
                                             file_type = file_type,
                                             path_type = path_type,
                                             ignore_case = ignore_case)
    self.add_item(item, negate = negate)

  def add_item_re(self,
                  expression,
                  file_type = None,
                  path_type = None,
                  ignore_case = False,
                  negate = False):
    item = bf_file_matcher_item_re(expression,
                                   file_type = file_type,
                                   path_type = path_type,
                                   ignore_case = ignore_case)
    self.add_item(item, negate = negate)
    
  def add_item_callable(self, callable_, file_type = None, path_type = None, negate = False):
    item = bf_file_matcher_item_callable(callable_,
                                         file_type = file_type,
                                         path_type = path_type)
    self.add_item(item, negate = negate)

  def add_item_datetime(self, date, comparison_type, file_type = None, negate = False):
    item = bf_file_matcher_item_datetime(date, comparison_type, file_type = file_type)
    self.add_item(item, negate = negate)

  def add_item_attr(self, attrs, file_type = None, negate = False):
    item = bf_file_matcher_item_attr(attrs, file_type = file_type)
    self.add_item(item, negate = negate)

  def add_item_metadata(self, metadatas, file_type = None, negate = False):
    item = bf_file_matcher_item_metadata(metadatas, file_type = file_type)
    self.add_item(item, negate = negate)
    
  def match(self, entry, match_type = None):
    check.check_bf_entry(entry)
    match_type = check.check_bf_file_matcher_mode(match_type, allow_none = True)
    match_type = match_type or bf_file_matcher_mode.ANY
    
    self._log.log_d(f'match: entry={entry.relative_filename} match_type={match_type.name}')
    
    if self.empty:
      self._log.log_d(f'match: no matchers found')
      return True
    
    func_map = {
      bf_file_matcher_mode.ALL: self._match_all,
      bf_file_matcher_mode.ANY: self._match_any,
      bf_file_matcher_mode.NONE: self._match_none,
    }
    func = func_map[match_type]
    return func(entry, self._matchers)

  def match_entries(self, entries, match_type = None):
    entries = check.check_bf_entry_list(entries)

    if self.empty:
      return entries[:]

    result = bf_entry_list()
    for entry in entries:
      match_result = self.match(entry, match_type = match_type)
      if match_result:
        result.append(entry)
    return result
  
  @classmethod
  def _match_any(clazz, entry, matchers):
    num = len(matchers)
    for i, next_matcher in enumerate(matchers, start = 1):
      matched = next_matcher.matcher.match(entry)
      if next_matcher.negate:
        matched = not matched
      clazz._log.log_d(f'_match_any: {i} of {num}: entry={entry.relative_filename} matcher={next_matcher.matcher} negate={next_matcher.negate} => {matched}')
      if matched:
        return True
    return False

  @classmethod
  def _match_all(clazz, entry, matchers):
    num = len(matchers)
    for i, next_matcher in enumerate(matchers, start = 1):
      matched = next_matcher.matcher.match(entry)
      if next_matcher.negate:
        matched = not matched
      clazz._log.log_d(f'_match_all: {i} of {num}:  entry={entry.relative_filename} matcher={next_matcher.matcher} negate={next_matcher.negate} => {matched}')
      if not matched:
        return False
    return True

  @classmethod
  def _match_none(clazz, entry, matchers):
    num = len(matchers)
    for i, next_matcher in enumerate(matchers, start = 1):
      matched = next_matcher.matcher.match(entry)
      if next_matcher.negate:
        matched = not matched
      clazz._log.log_d(f'_match_none: {i} of {num}:  entry={entry.relative_filename} matcher={next_matcher.matcher} negate={next_matcher.negate} => {matched}')
      if matched:
        return False
    return True
      
check.register_class(bf_file_matcher, include_seq = False)

class bf_cli_file_matcher(bcli_type_i):

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
