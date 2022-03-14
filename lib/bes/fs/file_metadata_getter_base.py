#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

from bes.common.check import check

class file_metadata_getter_base(with_metaclass(ABCMeta, object)):

  @abstractmethod
  def name(self):
    'Return the name of this getter.'
    raise NotImplemented('name')
  
  @abstractmethod
  def key_name(self):
    'Return the key name.'
    raise NotImplemented('key_name')
  
  @abstractmethod
  def get_value(self, filename):
    'Get the metadata value from filename.'
    raise NotImplemented('get_value')

check.register_class(file_metadata_getter_base, name = 'file_metadata_getter', include_seq = False)
