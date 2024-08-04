#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime

import ast

from bes.system.check import check

from ..bcli_type_i import bcli_type_i

class bcli_type_datetime(bcli_type_i):

  @classmethod
  #@abstractmethod
  def name_str(clazz):
    return 'datetime'

  @classmethod
  #@abstractmethod
  def type_function(clazz):
    return datetime

  @classmethod
  #@abstractmethod
  def parse(clazz, text):
    if text == None:
      return None
    return datetime.fromisoformat(text)

  @classmethod
  #@abstractmethod
  def check(clazz, value, allow_none = False):
    return check.check_datetime(value, allow_none = allow_none)
