#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.number_util import number_util
from bes.system.check import check

from ..bcli_type_i import bcli_type_i

class bcli_type_str(bcli_type_i):

  @classmethod
  #@abstractmethod
  def name_str(clazz):
    return 'str'

  @classmethod
  #@abstractmethod
  def type_function(clazz):
    return str

  @classmethod
  #@abstractmethod
  def parse(clazz, text):
    return text

  @classmethod
  #@abstractmethod
  def check(clazz, value, allow_none = False):
    return check.check_str(value, allow_none = allow_none)
