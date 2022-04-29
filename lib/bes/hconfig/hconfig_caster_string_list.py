#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..text.string_list import string_list
from ..text.string_lexer import string_lexer_options

from ..system.check import check

from .hconfig_type_base import hconfig_type_base

class hconfig_caster_string_list(hconfig_type_base):

  @classmethod
  #@abstractmethod
  def cast_value(clazz, value):
    'Cast a value.'
    check.check_string(value)

    return string_list.parse(value, string_lexer_options.KEEP_QUOTES | string_lexer_options.IGNORE_COMMENTS)
