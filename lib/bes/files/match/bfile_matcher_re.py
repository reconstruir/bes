#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from bes.system.check import check
from bes.property.cached_property import cached_property

from .bfile_matcher_base import bfile_matcher_base
from .bfile_filename_matcher_options import bfile_filename_matcher_options

class bfile_matcher_re(bfile_matcher_base):

  def __init__(self, expressions, options):
    check.check_bfile_filename_matcher_options(options)

    self._expressions = self.check_sequence(expressions)
    self._options = options

  #@abstractmethod
  def match(self, entry):
    'Return True if filename matches.'
    check.check_bfile_entry(entry)

    return self._match_sequence(entry,
                                self._expressions,
                                self._options.match_type,
                                self._match_function,
                                self._options)

  @classmethod
  def _match_function(clazz, entry, expression, options):
    flags = 0
    if options.ignore_case:
      flags = re.IGNORECASE
    filename = clazz.filename_for_match(entry, False, options.basename_only)
    for next_entry in re.finditer(expression, filename, flags):
      if next_entry:
        return True
    return False
