#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum_util.checked_int_flag_enum import checked_int_flag_enum
from bes.bcli.bcli_type_i import bcli_type_i
from bes.system.check import check

class bf_file_type(checked_int_flag_enum):
  FILE = 0x02
  DIR = 0x04
  LINK = 0x08
  DEVICE = 0x10
  ANY = FILE | DIR | LINK | DEVICE
  FILE_OR_LINK = FILE | LINK
  ANY_FILE = FILE | LINK | DEVICE

  def mask_matches(self, mask):
    return (self & mask) != 0
  
bf_file_type.register_check_class()

class bf_cli_file_type(bcli_type_i):

  #@abstractmethod
  def name_str(self):
    return 'bf_file_type'

  #@abstractmethod
  def type_function(self):
    return lambda: bf_file_type

  #@abstractmethod
  def parse(self, text):
    return bf_file_type.parse_string(text)

  #@abstractmethod
  def check(self, value, allow_none = False):
    return check.check_bf_file_type(value, allow_none = allow_none)
