#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import fnmatch

from bes.system.check import check
from bes.system.log import logger
from bes.property.cached_property import cached_property

from .bfile_matcher_base import bfile_matcher_base
from .bfile_matcher_options import bfile_matcher_options

class bfile_matcher_fnmatch(bfile_matcher_base):

  _log = logger('match')
  
  def __init__(self, pattern):
    check.check_string(pattern)

    self._pattern = pattern

  def __str__(self):
    return f'bfile_matcher_fnmatch("{self._pattern}")'
    
  @cached_property
  def _pattern_lowercase(self):
    return self._pattern.lower()

  #@abstractmethod
  def match(self, entry, options):
    'Return True if filename matches.'
    check.check_bfile_entry(entry)
    check.check_bfile_matcher_options(options)

    pattern = self._pattern_lowercase if options.ignore_case else self._pattern
    filename = entry.filename_for_matcher(options.path_type, options.ignore_case)
    matched = fnmatch.fnmatch(filename, pattern)
    self._log.log_d(f'{self}: match({entry.filename}) filename={filename} pattern="{pattern}" => {matched}')
    return matched
