#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.number_util import number_util
from bes.system.check import check

from ..bcli_type_i import bcli_type_i

class bcli_type_str(bcli_type_i):

  #@abstractmethod
  def name_str(self):
    return 'str'

  #@abstractmethod
  def type_function(self):
    return lambda: str

  #@abstractmethod
  def parse(self, text):
    return text

  #@abstractmethod
  def check(self, value, allow_none = False):
    return check.check_str(value, allow_none = allow_none)
