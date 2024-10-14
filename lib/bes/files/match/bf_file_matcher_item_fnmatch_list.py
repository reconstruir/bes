#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import fnmatch

from bes.system.check import check
from bes.system.log import logger
from bes.property.cached_property import cached_property

from .bf_file_matcher_item_base import bf_file_matcher_item_base
from .bf_file_matcher_type import bf_file_matcher_type

class bf_file_matcher_item_fnmatch_list(bf_file_matcher_item_base):

  _log = logger('bf_file_matcher')
  
  def __init__(self, patterns, list_match_type, file_type = None, path_type = None, ignore_case = False):
    super().__init__(file_type, path_type)
    self._patterns = check.check_string_seq(patterns)[:]
    self._list_match_type = check.check_bf_file_matcher_type(list_match_type)
    self._ignore_case = ignore_case

  def __str__(self):
    return f'fmi_fnmatch_list("{self._patterns}")'
    
  @cached_property
  def _patterns_lowercase(self):
    return [ pattern.lower() for pattern in self._patterns ]

  #@abstractmethod
  def match(self, entry):
    'Return True if filename matches.'
    check.check_bf_entry(entry)

    matched_type = self.match_file_type(entry)
    matched = False
    if matched_type:
      patterns = self._patterns_lowercase if self._ignore_case else self._patterns
      filename = entry.filename_for_matcher(self.path_type, self._ignore_case)
      fnmatcher = fnmatch.fnmatch if self._ignore_case else fnmatch.fnmatchcase
      func_map = {
        bf_file_matcher_type.ALL: self._match_all,
        bf_file_matcher_type.ANY: self._match_any,
        bf_file_matcher_type.NONE: self._match_none,
      }
      func = func_map[self._list_match_type]
      matched = func(filename, self._patterns, fnmatcher)
      import pprint
      patterns = pprint.pformat(patterns)
      #self._log.log_e(f'match({entry.root_dir},{entry.filename}) {filename} list_match_type={self._list_match_type.name} filename={filename} patterns="{patterns}" => {matched}')
    self._log.log_d(f'match({entry.root_dir}-{filename}) {filename} list_match_type={self._list_match_type.name} filename={filename} => {matched}')
    return matched

  @classmethod
  def _match_any(clazz, filename, patterns, fnmatcher):
    num = len(patterns)
    for i, next_pattern in enumerate(patterns, start = 1):
      matched = fnmatcher(filename, next_pattern)
      clazz._log.log_d(f'_match_any: {i} of {num}: filename={filename} pattern={next_pattern} => {matched}')
      if matched:
        return True
    return False

  @classmethod
  def _match_all(clazz, filename, patterns, fnmatcher):
    num = len(patterns)
    for i, next_pattern in enumerate(patterns, start = 1):
      matched = fnmatcher(filename, next_pattern)
      clazz._log.log_d(f'_match_all: {i} of {num}: filename={filename} pattern={next_pattern} => {matched}')
      if not matched:
        return False
    return True
    
  @classmethod
  def _match_none(clazz, filename, patterns, fnmatcher):
    num = len(patterns)
    for i, next_pattern in enumerate(patterns, start = 1):
      matched = fnmatcher(filename, next_pattern)
      clazz._log.log_d(f'_match_none: {i} of {num}:  entry={filename} pattern={next_pattern} => {matched}')
      if matched:
        return False
    return True
  
  #@abstractmethod
  def clone(self):
    'Clone the matcher item.'
    return bf_file_matcher_item_fnmatch_list(self._patterns[:],
                                             self._list_match_type,
                                             file_type = self.file_type,
                                             path_type = self.path_type,
                                             ignore_case = self._ignore_case)
