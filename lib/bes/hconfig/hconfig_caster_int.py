#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..common.number_util import number_util
from ..system.check import check

from .hconfig_caster_base import hconfig_caster_base
from .hconfig_error import hconfig_error

class hconfig_caster_int(hconfig_caster_base):

  @classmethod
  #@abstractmethod
  def cast_value(clazz, value):
    'Cast a value.'
    if not number_util.string_is_int(value):
      raise hconfig_error(f'Not an int: {value}')
    return int(value)
