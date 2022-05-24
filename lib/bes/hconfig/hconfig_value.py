#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.log import logger
from ..system.check import check

from .hconfig_error import hconfig_error

class hconfig_value(object):

  @classmethod
  def get_with_default(clazz, value, field, default_value):
    try:
      return getattr(value, field)
    except hconfig_error as ex:
      return default_value
