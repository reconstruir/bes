#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from .bf_file_matcher_item_i import bf_file_matcher_item_i
from .bf_file_matcher_options import bf_file_matcher_options

class bf_file_matcher_item_callable(bf_file_matcher_item_i):

  _log = logger('bf_file_matcher')
  
  def __init__(self, callable_):
    check.check_callable(callable_)
    
    self._callable = callable_

  def __str__(self):
    return f'bf_file_matcher_item_callable("{self._callable}")'
    
  #@abstractmethod
  def match(self, entry, options):
    'Return True if filename matches.'
    check.check_bf_entry(entry)
    check.check_bf_file_matcher_options(options)

    filename = entry.filename_for_matcher(options.path_type, options.ignore_case)
    matched = self._callable(entry, filename)
    self._log.log_d(f'{self}: match({entry.filename}, {entry.root_dir}) filename={filename} => {matched}')
    return matched

  #@abstractmethod
  def clone(self):
    'Clone the matcher item.'
    return bf_file_matcher_item_callable(self._callable)
  
