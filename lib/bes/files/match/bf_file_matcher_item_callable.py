#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from .bf_file_matcher_item_base import bf_file_matcher_item_base

class bf_file_matcher_item_callable(bf_file_matcher_item_base):

  _log = logger('bf_file_matcher')
  
  def __init__(self, callable_, file_type = None, path_type = None):
    super().__init__(file_type, path_type)
    self._callable = check.check_callable(callable_)

  def __str__(self):
    return f'fmi_callable("{self._callable}")'
    
  #@abstractmethod
  def match(self, entry):
    'Return True if filename matches.'
    check.check_bf_entry(entry)

    matched_type = self.match_file_type(entry)
    matched = False
    if matched_type:
      filename = entry.filename_for_matcher(self.path_type, False)
      matched = self._callable(filename)
    self._log.log_d(f'{self}: match({entry.relative_filename}) => {matched}')
    return matched

  #@abstractmethod
  def clone(self):
    'Clone the matcher item.'
    return bf_file_matcher_item_callable(self._callable,
                                         file_type = self.file_type)
  
