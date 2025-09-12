#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from ..system.check import check

class file_metadata_getter_base(object, metaclass = ABCMeta):

  @classmethod
  @abstractmethod
  def name(clazz):
    'Return the name of this getter.'
    raise NotImplementedError('name')
  
  @abstractmethod
  def get_value(self, filename):
    'Get a metadata value from filename and return it encoded as bytes.'
    raise NotImplementedError('get_value')

  @abstractmethod
  def decode_value(self, value):
    'Decode a value given as bytes.'
    raise NotImplementedError('decode_value')
  
check.register_class(file_metadata_getter_base, name = 'file_metadata_getter', include_seq = False)
