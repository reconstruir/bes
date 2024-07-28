#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_type_i import bcli_type_i
from bes.enum_util.checked_enum import checked_enum
from bes.system.check import check

class bf_match_type(checked_enum):
  ALL = 'all'
  ANY = 'any'
  NONE = 'none'
  
bf_match_type.register_check_class()

class bf_cli_match_type(bcli_type_i):

  #@abstractmethod
  def name_str(self):
    return 'bf_match_type'

  #@abstractmethod
  def type_function(self):
    return lambda: bf_match_type

  #@abstractmethod
  def parse(self, text):
    return bf_match_type.parse_string(text)

  #@abstractmethod
  def check(self, value, allow_none = False):
    return check.check_bf_match_type(value, allow_none = allow_none)
