#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import ast

from bes.system.check import check

from ..bcli_type_i import bcli_type_i

class bcli_type_list(bcli_type_i):

  #@abstractmethod
  def name_str(self):
    return 'list'

  #@abstractmethod
  def type_function(self):
    return lambda: list

  #@abstractmethod
  def parse(self, text):
    return ast.literal_eval(text)

  #@abstractmethod
  def check(self, value, allow_none = False):
    return check.check_list(value, allow_none = allow_none)
