#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..common.bool_util import bool_util
from ..system.check import check

from .hconfig_caster_base import hconfig_caster_base

class hconfig_caster_bool(hconfig_caster_base):

  @classmethod
  #@abstractmethod
  def cast_value(clazz, value):
    'Cast a value.'
    return bool_util.parse_bool(value)
