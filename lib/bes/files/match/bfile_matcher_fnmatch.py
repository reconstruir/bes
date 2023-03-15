#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import fnmatch

from bes.system.check import check
from bes.property.cached_property import cached_property

from .bfile_matcher_base import bfile_matcher_base
from .bfile_matcher_options import bfile_matcher_options

class bfile_matcher_fnmatch(bfile_matcher_base):

  def __init__(self, patterns):
    self._patterns = self.check_sequence(patterns)

  @cached_property
  def _patterns_lowercase(self):
    return [ p.lower() for p in self._patterns ]

  #@abstractmethod
  def match(self, entry, options):
    'Return True if filename matches.'
    check.check_bfile_entry(entry)
    check.check_bfile_matcher_options(options)

    if options.ignore_case:
      patterns = self._patterns_lowercase
    else:
      patterns = self._patterns

    return self._match_sequence(entry,
                                patterns,
                                options.match_type,
                                self._match_function,
                                options)

  @classmethod
  def _match_function(clazz, entry, pattern, options):
    filename = entry.filename_for_matcher(options.path_type, options.ignore_case)
    return fnmatch.fnmatch(filename, pattern)
  
