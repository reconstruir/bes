#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

from bes.system.check import check

from .bfile_filename_match_type import bfile_filename_match_type
from .bfile_filename_matcher_options import bfile_filename_matcher_options

class bfile_filename_matcher_base(with_metaclass(ABCMeta, object)):

  @abstractmethod
  def match(self, filename, options):
    'Return True if filename matches.'
    raise NotImplemented('match')

check.register_class(bfile_filename_matcher_base, name = 'bfile_filename_matcher')
