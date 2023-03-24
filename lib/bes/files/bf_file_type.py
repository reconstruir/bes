#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum_util.checked_int_flag_enum import checked_int_flag_enum

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
