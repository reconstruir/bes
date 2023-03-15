#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from .bfile_matcher_base import bfile_matcher_base
from .bfile_matcher_options import bfile_matcher_options

class bfile_matcher_callable(bfile_matcher_base):

  def __init__(self, callables):
    self._callables = self.check_callables(callables)

  #@abstractmethod
  def match(self, entry, options):
    'Return True if filename matches.'
    check.check_bfile_entry(entry)
    check.check_bfile_matcher_options(options)

    return self._match_sequence(entry,
                                self._callables,
                                options.match_type,
                                self._match_function,
                                options)

  @classmethod
  def _match_function(clazz, entry, callable_, options):
    filename = entry.filename_for_matcher(options.path_type, options.ignore_case)
    return callable_(filename)

  @classmethod
  def check_callables(clazz, seq):
    if check.is_callable_seq(seq):
      return [ c for c in seq ]
    elif check.is_callable(seq):
      return [ seq ]
    raise TypeError(f'seq should be either be callable or sequence of callable: "{seq}" - {type(seq)}')
