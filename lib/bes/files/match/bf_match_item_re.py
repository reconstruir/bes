#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from bes.system.check import check
from bes.system.log import logger
from bes.property.cached_property import cached_property

from .bf_match_item_i import bf_match_item_i
from .bf_match_options import bf_match_options

class bf_match_item_re(bf_match_item_i):

  _log = logger('match')
  
  def __init__(self, expression):
    check.check_string(expression)

    self._expression = expression

  def __str__(self):
    return f'bf_match_item_re("{self._expression}")'
    
  #@abstractmethod
  def match(self, entry, options):
    'Return True if filename matches.'
    check.check_bf_entry(entry)
    check.check_bf_match_options(options)

    flags = 0
    if options.ignore_case:
      flags = re.IGNORECASE
    filename = entry.filename_for_matcher(options.path_type, False)
    matched = False
    for next_entry in re.finditer(self._expression, filename, flags):
      if next_entry:
        matched = True
        break
    self._log.log_d(f'{self}: match({entry.filename}) filename={filename} expression="{self._expression}" => {matched}')
    return matched
