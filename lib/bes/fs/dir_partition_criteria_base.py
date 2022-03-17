#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

from bes.common.check import check

class dir_partition_criteria_base(with_metaclass(ABCMeta, object)):

  @abstractmethod
  def classify(self, filename):
    'Return a string that classifies filename for dir partition.'
    raise NotImplemented('classify')
  
check.register_class(dir_partition_criteria_base, name = 'dir_partition_criteria', include_seq = False)
