#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from ..bfile_date_comparison_type import bfile_date_comparison_type

from .bfile_matcher_base import bfile_matcher_base
from .bfile_matcher_options import bfile_matcher_options

class bfile_matcher_timedelta(bfile_matcher_base):

  _log = logger('match')
  
  def __init__(self, delta, comparison_type):
    self._delta = check.check_timedelta(delta)
    self._comparison_type = check.check_bfile_date_comparison_type(comparison_type)

  def __str__(self):
    return f'bfile_matcher_timedelta({self._delta}, {self._comparison_type})'
    
  #@abstractmethod
  def match(self, entry, options):
    'Return True if filename matches.'
    check.check_bfile_entry(entry)
    check.check_bfile_matcher_options(options)

    matched = entry.modification_date_matches_delta(self._delta, self._comparison_type)
    self._log.log_d(f'{self}: match({entry.filename}) delta={self._delta} comparison_type={self._comparison_type.name} => {matched}')
    return matched
