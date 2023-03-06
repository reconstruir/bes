#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.property.cached_property import cached_property

from .bfile_matcher_sequence import bfile_matcher_sequence

class bfile_matcher_patterns(bfile_matcher_sequence):

  def __init__(self, patterns, options):
    check.check_bfile_filename_matcher_options(options)

    if check.is_string_seq(patterns):
      self._patterns = [ p for p in patterns ]
    elif check.is_string(patterns):
      self._patterns = [ patterns ]
    else:
      raise TypeError(f'patterns should be a string or string sequence: "{patterns}" - {type(patterns)}')
    self._options = options

  @property
  def patterns(self):
    return self._patterns
  
  @cached_property
  def patterns_lowercase(self):
    return [ p.lowercase() for p in self._patterns ]

  @cached_property
  def patterns_for_match(self):
    if self._options.ignore_case:
      return self.patterns_lowercase
    else:
      return self.patterns
  
  def _match_patterns(self, entry, match_function, dont_ignore_case = False):
    check.check_bfile_entry(entry)
    check.check_callable(match_function)

    ignore_case = self._options.ignore_case and not dont_ignore_case
    basename_only = self._options.basename_only
    
    def _match_function(entry, pattern):
      if ignore_case and basename_only:
        filename = entry.basename_lowercase
      elif ignore_case:
        filename = entry.filename_lowercase
      elif basename_only:
        filename = entry.basename
      else:
        filename = entry.filename
      return match_function(filename, pattern)

    return self._match_sequence(entry,
                                self.patterns_for_match,
                                self._options.match_type,
                                _match_function)
