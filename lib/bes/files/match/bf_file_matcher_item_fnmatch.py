#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import fnmatch

from bes.system.check import check
from bes.system.log import logger
from bes.property.cached_property import cached_property

from .bf_file_matcher_item_i import bf_file_matcher_item_i
from .bf_file_matcher_options import bf_file_matcher_options

class bf_file_matcher_item_fnmatch(bf_file_matcher_item_i):

  _log = logger('bf_file_matcher')
  
  def __init__(self, pattern):
    check.check_string(pattern)

    self._pattern = pattern

  def __str__(self):
    return f'bf_file_matcher_item_fnmatch("{self._pattern}")'
    
  @cached_property
  def _pattern_lowercase(self):
    return self._pattern.lower()

  #@abstractmethod
  def match(self, entry, options):
    'Return True if filename matches.'
    check.check_bf_entry(entry)
    check.check_bf_file_matcher_options(options)

    pattern = self._pattern_lowercase if options.ignore_case else self._pattern
    filename = entry.filename_for_matcher(options.path_type, options.ignore_case)
    matched = fnmatch.fnmatchcase(filename, pattern)
    self._log.log_d(f'{self}: match({entry.filename}) filename={filename} pattern="{pattern}" => {matched}')
    return matched

  #@abstractmethod
  def clone(self):
    'Clone the matcher item.'
    return bf_file_matcher_item_fnmatch(self._pattern)
