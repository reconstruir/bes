#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from .bfile_matcher_base import bfile_matcher_base
from .bfile_matcher_options import bfile_matcher_options

class bfile_matcher_callable(bfile_matcher_base):

  _log = logger('match')
  
  def __init__(self, callable_):
    check.check_callable(callable_)
    
    self._callable = callable_

  def __str__(self):
    return f'bfile_matcher_callable("{self._callable}")'
    
  #@abstractmethod
  def match(self, entry, options):
    'Return True if filename matches.'
    check.check_bfile_entry(entry)
    check.check_bfile_matcher_options(options)

    filename = entry.filename_for_matcher(options.path_type, options.ignore_case)
    matched = self._callable(filename)
    self._log.log_d(f'{self}: match({entry.filename}, {entry.root_dir}) filename={filename} => {matched}')
    return matched
