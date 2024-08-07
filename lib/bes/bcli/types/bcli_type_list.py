#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import ast

from bes.system.check import check
from bes.common.string_util import string_util

from ..bcli_type_i import bcli_type_i

class bcli_type_list(bcli_type_i):

  @classmethod
  #@abstractmethod
  def name_str(clazz):
    return 'list'

  @classmethod
  #@abstractmethod
  def type_function(clazz):
    return list

  @classmethod
  #@abstractmethod
  def parse(clazz, text):
    if text == None:
      value = None
    if check.is_string(text):
      value = ast.literal_eval(text)
    elif check.is_seq(text):
      value = list(text)
    else:
      raise TypeError(f'Unknown type {type(text)} for "{text}"')
    return value

  @classmethod
  #@abstractmethod
  def check(clazz, value, allow_none = False):
    return check.check_list(value, allow_none = allow_none)
