#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.common.check import check

class file_checksum_getter_base(with_metaclass(ABCMeta, object)):

  @abstractmethod
  def checksum(self, algorithm, filename):
    'Return the checksum for filename using algorithm.'
    pass

check.register_class(file_checksum_getter_base, 'file_checksum_getter')
