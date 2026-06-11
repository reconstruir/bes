#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from ..bcli_type_i import bcli_type_i

class bcli_type_callable(bcli_type_i):

  @classmethod
  #@abstractmethod
  def name_str(clazz):
    return 'callable'

  @classmethod
  #@abstractmethod
  def type_function(clazz):
    return callable

  @classmethod
  #@abstractmethod
  def parse(clazz, text):
    if text is None:
      return None
    if not isinstance(text, str):
      return text
    if text == 'None':
      return None
    raise ValueError(f'callable type cannot be parsed from string: "{text}"')

  @classmethod
  #@abstractmethod
  def check(clazz, value, allow_none = False):
    return check.check_callable(value, allow_none = allow_none)
