#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from bes.system.check import check
from bes.property.cached_property import cached_property

from .bfile_matcher_base import bfile_matcher_base
from .bfile_matcher_options import bfile_matcher_options

class bfile_matcher_re(bfile_matcher_base):

  def __init__(self, expressions):
    self._expressions = self.check_sequence(expressions)

  #@abstractmethod
  def match(self, entry, options):
    'Return True if filename matches.'
    check.check_bfile_entry(entry)
    check.check_bfile_matcher_options(options)

    return self._match_sequence(entry,
                                self._expressions,
                                options.match_type,
                                self._match_function,
                                options)

  @classmethod
  def _match_function(clazz, entry, expression, options):
    flags = 0
    if options.ignore_case:
      flags = re.IGNORECASE
    filename = entry.filename_for_matcher(options.path_type, False)
    for next_entry in re.finditer(expression, filename, flags):
      if next_entry:
        return True
    return False
