#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.property.cached_property import cached_property

from .bfile_filename_matcher_base import bfile_filename_matcher_base
from .bfile_filename_matcher_options import bfile_filename_matcher_options
from .bfile_filename_match_type import bfile_filename_match_type

class bfile_filename_matcher_patterns(bfile_filename_matcher_base):

  def __init__(self, patterns, match_type):
    match_type = check.check_bfile_filename_match_type(match_type)

    if check.is_string_seq(patterns):
      self._patterns = [ p for p in patterns ]
    elif check.is_string(patterns):
      self._patterns = [ patterns ]
    else:
      raise TypeError(f'patterns should be a string or string sequence: "{patterns}" - {type(patterns)}')
    self._match_type = match_type

  @property
  def patterns(self):
    return self._patterns
  
  @cached_property
  def patterns_lowercase(self):
    return [ p.lowercase() for p in self._patterns ]

  def _match_patterns(self, filename, match_function, options):
    'Return True if filename matches.'
    check.check_string(filename)
    check.check_callable(match_function)
    check.check_bfile_filename_matcher_options(options)

    if options.basename_only:
      filename_for_match = path.basename(filename)
    else:
      filename_for_match = filename
    
    if options.ignore_case:
      filename_for_match = filename_for_match.lower()
      patterns_for_match = self.patterns_lowercase
    else:
      filename_for_match = filename
      patterns_for_match = self.patterns

    func_map = {
      bfile_filename_match_type.ALL: self._match_all,
      bfile_filename_match_type.ANY: self._match_any,
      bfile_filename_match_type.NONE: self._match_none,
    }
    func = func_map[self._match_type]
    return func(match_function, filename_for_match, patterns_for_match)

  @staticmethod
  def _match_any(match_function, filename, patterns):
    for pattern in patterns:
      if match_function(filename, pattern):
        return True
    return False

  @staticmethod
  def _match_all(match_function, filename, patterns):
    for pattern in patterns:
      if not match_function(filename, pattern):
        return False
    return True

  @staticmethod
  def _match_none(match_function, filename, patterns):
    for pattern in patterns:
      if match_function(filename, pattern):
        return False
    return True
  
