#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import fnmatch

from bes.system.check import check
from bes.system.log import logger
from bes.property.cached_property import cached_property

from .bf_match_item_base import bf_match_item_base
from .bf_match_options import bf_match_options

class bf_match_item_fnmatch(bf_match_item_base):

  _log = logger('match')
  
  def __init__(self, pattern):
    check.check_string(pattern)

    self._pattern = pattern

  def __str__(self):
    return f'bf_match_item_fnmatch("{self._pattern}")'
    
  @cached_property
  def _pattern_lowercase(self):
    return self._pattern.lower()

  #@abstractmethod
  def match(self, entry, options):
    'Return True if filename matches.'
    check.check_bf_entry(entry)
    check.check_bf_match_options(options)

    pattern = self._pattern_lowercase if options.ignore_case else self._pattern
    filename = entry.filename_for_matcher(options.path_type, options.ignore_case)
    matched = fnmatch.fnmatchcase(filename, pattern)
    self._log.log_d(f'{self}: match({entry.filename}) filename={filename} pattern="{pattern}" => {matched}')
    return matched
