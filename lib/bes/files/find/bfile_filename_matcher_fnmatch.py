#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import fnmatch

from bes.system.check import check
from bes.common.object_util import object_util
from bes.property.cached_property import cached_property

from .bfile_filename_matcher_patterns import bfile_filename_matcher_patterns

class bfile_filename_matcher_fnmatch(bfile_filename_matcher_patterns):

  #@abstractmethod
  def match(self, filename, options):
    'Return True if filename matches.'
    check.check_string(filename)
    check.check_bfile_filename_matcher_options(options)

    return self._match_patterns(filename, fnmatch.fnmatch, options)
