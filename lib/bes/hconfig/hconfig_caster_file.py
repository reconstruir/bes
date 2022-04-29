#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from ..system.check import check

from .hconfig_type_base import hconfig_type_base
from .hconfig_error import hconfig_error

class hconfig_caster_file(hconfig_type_base):

  @classmethod
  #@abstractmethod
  def cast_value(clazz, value):
    return path.expanduser(value)
