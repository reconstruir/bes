#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from bes.system.compat import with_metaclass
from bes.system.check import check

class bfile_metadata_getter_base(with_metaclass(ABCMeta, object)):

  @classmethod
  @abstractmethod
  def domain(clazz):
    'Return domain name.'
    raise NotImplemented('domain')
  
  @classmethod
  @abstractmethod
  def keys(clazz):
    'Return a dictionary of keys and versions this getter supports.'
    raise NotImplemented('keys')
  
  @abstractmethod
  def get_value(self, filename, domain, key, version):
    'Get a metadata value from filename and return it encoded as bytes.'
    raise NotImplemented('get_value')

  @abstractmethod
  def decode_value(self, value):
    'Decode a value given as bytes.'
    raise NotImplemented('decode_value')
  
check.register_class(bfile_metadata_getter_base, name = 'bfile_metadata_getter', include_seq = False)
