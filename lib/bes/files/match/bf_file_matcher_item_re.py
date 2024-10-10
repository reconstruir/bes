#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from bes.system.check import check
from bes.system.log import logger

from ..bf_file_type import bf_file_type
from ..bf_path_type import bf_path_type

from .bf_file_matcher_item_base import bf_file_matcher_item_base

class bf_file_matcher_item_re(bf_file_matcher_item_base):

  _log = logger('bf_file_matcher')
  
  def __init__(self, expression, file_type = None, path_type = None, ignore_case = False):
    super().__init__(file_type, path_type)
    check.check_string(expression)

    self._expression = expression
    self._ignore_case = ignore_case

  def __str__(self):
    return f'bf_file_matcher_item_re("{self._expression}")'
    
  #@abstractmethod
  def match(self, entry):
    'Return True if filename matches.'
    check.check_bf_entry(entry)

    matched_type = self.match_file_type(entry)
    matched = False
    if matched_type:
      flags = 0
      if self._ignore_case:
        flags = re.IGNORECASE
      filename = entry.filename_for_matcher(self.path_type, False)
      matched = False
      for next_entry in re.finditer(self._expression, filename, flags):
        if next_entry:
          matched = True
          break
      self._log.log_d(f'{self}: match({entry.relative_filename}) expression="{self._expression}" => {matched}')
    return matched

  #@abstractmethod
  def clone(self):
    'Clone the matcher item.'
    return bf_file_matcher_item_re(self._expression,
                                   file_type = self.file_type,
                                   path_type = self.path_type,
                                   ignore_case = self._ignore_case)
