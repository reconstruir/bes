#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import fnmatch

from bes.system.check import check
from bes.property.cached_property import cached_property

from .bfile_matcher_base import bfile_matcher_base
from .bfile_filename_matcher_options import bfile_filename_matcher_options

class bfile_matcher_fnmatch(bfile_matcher_base):

  def __init__(self, patterns, options):
    check.check_bfile_filename_matcher_options(options)

    self._patterns = self.check_sequence(patterns)
    self._options = options

  @cached_property
  def _patterns_lowercase(self):
    return [ p.lowercase() for p in self._patterns ]

  #@abstractmethod
  def match(self, entry):
    'Return True if filename matches.'
    check.check_bfile_entry(entry)

    if self._options.ignore_case:
      patterns = self._patterns_lowercase
    else:
      patterns = self._patterns

    return self._match_sequence(entry,
                                patterns,
                                self._options.match_type,
                                self._match_function,
                                self._options)

  @classmethod
  def _match_function(clazz, entry, pattern, options):
    filename = clazz.filename_for_match(entry, options.ignore_case, options.basename_only)
    return fnmatch.fnmatch(filename, pattern)
  
