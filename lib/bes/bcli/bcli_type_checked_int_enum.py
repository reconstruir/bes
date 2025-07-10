#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from .bcli_type_i import bcli_type_i

class bcli_type_checked_int_enum(bcli_type_i):

  @classmethod
  #@abstractmethod
  def name_str(clazz):
    return clazz.__enum_class__.__name__

  @classmethod
  #@abstractmethod
  def type_function(clazz):
    return clazz.__enum_class__

  @classmethod
  #@abstractmethod
  def parse(clazz, text):
    #print(f'text={text} - {type(text)}')
    return clazz.__enum_class__.parse(text)

  @classmethod
  #@abstractmethod
  def check(clazz, value, allow_none = False):
    return check.check(value,  clazz.__enum_class__, allow_none = allow_none)
