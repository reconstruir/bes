#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from ..system.check import check

from .hconfig_type_base import hconfig_type_base
from .hconfig_error import hconfig_error
from .hconfig_type_file import hconfig_type_file

class hconfig_type_file_list(hconfig_type_base):

  @classmethod
  #@abstractmethod
  def cast(clazz, value, root):
    return [ hconfig_type_file.cast(x, root) for x in value ]
