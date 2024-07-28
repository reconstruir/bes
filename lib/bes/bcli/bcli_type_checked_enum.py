#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import ast

from bes.system.check import check

from ..bcli_type_i import bcli_type_i

class bcli_type_checked_enum(bcli_type_i, poto = some_class):

  #@abstractmethod
  def name_str(self):
    return some_class.name

  #@abstractmethod
  def type_function(self):
    return lambda: some_class

  #@abstractmethod
  def parse(self, text):
    return some_class.parse(text)

  #@abstractmethod
  def check(self, value, allow_none = False):
    return check.check(value, some_class, allow_none = allow_none)
