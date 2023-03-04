#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import fnmatch

from bes.system.check import check

from .bfile_matcher_patterns import bfile_matcher_patterns

class bfile_matcher_fnmatch(bfile_matcher_patterns):

  #@abstractmethod
  def match(self, entry):
    'Return True if filename matches.'
    check.check_bfile_entry(entry)

    return self._match_patterns(entry, fnmatch.fnmatch)
