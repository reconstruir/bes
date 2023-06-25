#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from .bf_attr_type_description_base import bf_attr_type_description_base
from .bf_attr_encoding import bf_attr_encoding

class bf_attr_type_description_bool(bf_attr_type_description_base):

  @classmethod
  #@abstractmethod
  def name(clazz):
    'Return the name for this type'
    return 'bool'

  @classmethod
  #@abstractmethod
  def encoder(clazz):
    'Return encoder function for this type'
    return bf_attr_encoding.encode_bool

  @classmethod
  #@abstractmethod
  def decoder(clazz):
    'Return decoder function for this type'
    return bf_attr_encoding.decode_bool

  @classmethod
  #@abstractmethod
  def checker(clazz):
    'Return checker function for this type'
    return check.check_bool
  
  @classmethod
  #@abstractmethod
  def description(clazz):
    'Return a description for this type.'
    return 'bool'
