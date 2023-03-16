#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from bes.system.check import check
from bes.property.cached_property import cached_property

from .bfile_matcher_base import bfile_matcher_base
from .bfile_matcher_options import bfile_matcher_options

class bfile_matcher_re(bfile_matcher_base):

  def __init__(self, expression):
    check.check_string(expression)

    self._expression = expression

  #@abstractmethod
  def match(self, entry, options):
    'Return True if filename matches.'
    check.check_bfile_entry(entry)
    check.check_bfile_matcher_options(options)

    flags = 0
    if options.ignore_case:
      flags = re.IGNORECASE
    filename = entry.filename_for_matcher(options.path_type, False)
    for next_entry in re.finditer(self._expression, filename, flags):
      if next_entry:
        print(f'matched {entry.filename} for {self._expression}')
        return True
    return False
