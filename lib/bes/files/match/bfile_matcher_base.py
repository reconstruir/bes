#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

from bes.system.check import check

from ..bfile_entry import bfile_entry

class bfile_matcher_base(with_metaclass(ABCMeta, object)):

  @abstractmethod
  def match(self, entry, options):
    'Return True if entry matches.'
    raise NotImplemented('match')
  
check.register_class(bfile_matcher_base, name = 'bfile_matcher', include_seq = False)
