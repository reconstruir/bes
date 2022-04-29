#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from ..system.check import check

from .hconfig_type_base import hconfig_type_base
from .hconfig_error import hconfig_error
from .hconfig_caster_file import hconfig_caster_file

class hconfig_caster_file_list(hconfig_type_base):

  @classmethod
  #@abstractmethod
  def cast_value(clazz, value):
    return [ hconfig_caster_file.cast_value(x) for x in value ]
