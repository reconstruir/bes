#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import fnmatch

from bes.system.check import check
from bes.system.log import logger

from .bf_file_matcher_item_i import bf_file_matcher_item_i
from .bf_file_matcher_options import bf_file_matcher_options
from .bf_file_matcher_type import bf_file_matcher_type

class bf_file_matcher_item_fnmatch_list(bf_file_matcher_item_i):

  _log = logger('bf_file_matcher')
  
  def __init__(self, patterns, match_type):
    check.check_string_seq(patterns)
    match_type = check.check_bf_file_matcher_type(match_type)

    self._patterns = patterns
    self._match_type = match_type

  def __str__(self):
    return f'bf_file_matcher_item_fnmatch_list("{self._patterns}")'
    
  @property
  def _patterns_lowercase(self):
    return [ pattern.lower() for pattern in self._patterns ]

  #@abstractmethod
  def match(self, entry, options):
    'Return True if filename matches.'
    check.check_bf_entry(entry)
    check.check_bf_file_matcher_options(options)

    patterns = self._patterns_lowercase if options.ignore_case else self._patterns
    filename = entry.filename_for_matcher(options.path_type, options.ignore_case)
    fnmatcher = fnmatch.fnmatch if options.ignore_case else fnmatch.fnmatchcase
    func_map = {
      bf_file_matcher_type.ALL: self._match_all,
      bf_file_matcher_type.ANY: self._match_any,
      bf_file_matcher_type.NONE: self._match_none,
    }
    func = func_map[self._match_type]
    matched = func(filename, self._patterns, fnmatcher)
    import pprint
    patterns = pprint.pformat(patterns)
    #self._log.log_e(f'match({entry.root_dir},{entry.filename}) {filename} match_type={self._match_type.name} filename={filename} patterns="{patterns}" => {matched}')
    self._log.log_d(f'match({entry.root_dir}-{filename}) {filename} match_type={self._match_type.name} filename={filename} => {matched}')
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
    return bf_file_matcher_item_fnmatch_list(self._patterns[:])
