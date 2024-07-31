#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import timedelta

import ast

from bes.system.check import check

from ..bcli_type_i import bcli_type_i

class bcli_type_timedelta(bcli_type_i):

  @classmethod
  #@abstractmethod
  def name_str(clazz):
    return 'timedelta'

  @classmethod
  #@abstractmethod
  def type_function(clazz):
    return timedelta

  @classmethod
  #@abstractmethod
  def parse(clazz, text):
    assert False

  @classmethod
  #@abstractmethod
  def check(clazz, value, allow_none = False):
    return check.check_timedelta(value, allow_none = allow_none)
