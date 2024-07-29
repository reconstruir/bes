#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import ast

from bes.system.check import check

from ..bcli_type_i import bcli_type_i

class bcli_type_tuple(bcli_type_i):

  @classmethod
  #@abstractmethod
  def name_str(clazz):
    return 'tuple'

  @classmethod
  #@abstractmethod
  def type_function(clazz):
    return tuple

  @classmethod
  #@abstractmethod
  def parse(clazz, text):
    return ast.literal_eval(text)

  @classmethod
  #@abstractmethod
  def check(clazz, value, allow_none = False):
    return check.check_tuple(value, allow_none = allow_none)
