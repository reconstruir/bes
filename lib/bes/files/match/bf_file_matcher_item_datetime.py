#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from ..bf_date_comparison_type import bf_date_comparison_type

from .bf_file_matcher_item_i import bf_file_matcher_item_i
from .bf_file_matcher_options import bf_file_matcher_options

class bf_file_matcher_item_datetime(bf_file_matcher_item_i):

  _log = logger('bf_file_matcher')
  
  def __init__(self, date, comparison_type):
    self._date = check.check_datetime(date)
    self._comparison_type = check.check_bf_date_comparison_type(comparison_type)

  def __str__(self):
    return f'bf_file_matcher_item_datetime({self._date}, {self._comparison_type})'
    
  #@abstractmethod
  def match(self, entry, options):
    'Return True if filename matches.'
    check.check_bf_entry(entry)
    check.check_bf_file_matcher_options(options)

    matched = entry.modification_date_matches(self._date, self._comparison_type)
    self._log.log_d(f'{self}: match({entry.filename}) date={self._date} comparison_type={self._comparison_type.name} => {matched}')
    return matched
