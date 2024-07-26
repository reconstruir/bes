#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.number_util import number_util
from bes.system.check import check

from ..bcli_type_i import bcli_type_i

class bcli_type_int(bcli_type_i):

  #@abstractmethod
  def name(self):
    return 'int'

  #@abstractmethod
  def type_function(self):
    return lambda: int

  #@abstractmethod
  def parse(self, text):
    return number_util.to_int(text)

  #@abstractmethod
  def check(self, value, allow_none = False):
    return check.check_int(value, allow_none = allow_none)
