#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import fnmatch

from bes.property.cached_property import cached_property
from bes.system.check import check
from bes.system.log import logger

from .bf_file_matcher_item_base import bf_file_matcher_item_base

class bf_file_matcher_item_fnmatch(bf_file_matcher_item_base):

  _log = logger('bf_file_matcher')
  
  def __init__(self, pattern, file_type = None, path_type = None, ignore_case = False):
    super().__init__(file_type, path_type)
    self._pattern = check.check_string(pattern)
    self._ignore_case = ignore_case

  def __str__(self):
    return f'bf_file_matcher_item_fnmatch("{self._pattern}")'
    
  @cached_property
  def _pattern_lowercase(self):
    return self._pattern.lower()

  #@abstractmethod
  def match(self, entry):
    'Return True if filename matches.'
    check.check_bf_entry(entry)

    matched_type = self.match_file_type(entry)
    matched = False
    if matched_type:
      pattern = self._pattern_lowercase if self._ignore_case else self._pattern
      filename = entry.filename_for_matcher(self.path_type, self._ignore_case)
      matched = fnmatch.fnmatchcase(filename, pattern)
    self._log.log_d(f'{self}: match({entry.relative_filename}) pattern="{pattern}" => {matched}')
    return matched

  #@abstractmethod
  def clone(self):
    'Clone the matcher item.'
    return bf_file_matcher_item_fnmatch(self._pattern,
                                        file_type = self.file_type,
                                        path_type = self.path_type,
                                        ignore_case = self._ignore_case)
