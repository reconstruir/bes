#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

from .hconfig_caster_base import hconfig_caster_base
from .hconfig_error import hconfig_error

class hconfig_caster_float(hconfig_caster_base):

  @classmethod
  #@abstractmethod
  def cast_value(clazz, value):
    'Cast a value.'
    try:
      return float(value)
    except ValueError as ex:
      raise hconfig_error(f'Not a float: {value}')
