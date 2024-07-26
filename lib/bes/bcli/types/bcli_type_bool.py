#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.bool_util import bool_util
from bes.system.check import check

from ..bcli_type_i import bcli_type_i

class bcli_type_bool(bcli_type_i):

  #@abstractmethod
  def name_str(self):
    return 'bool'

  #@abstractmethod
  def type_function(self):
    return lambda: bool

  #@abstractmethod
  def parse(self, text):
    return bool_util.parse_bool(text)

  #@abstractmethod
  def check(self, value, allow_none = False):
    return check.check_bool(value, allow_none = allow_none)