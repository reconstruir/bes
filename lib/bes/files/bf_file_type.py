#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum_util.checked_int_flag_enum import checked_int_flag_enum
from bes.bcli.bcli_type_checked_enum import bcli_type_checked_enum
from bes.system.check import check

class bf_file_type(checked_int_flag_enum):
  FILE = 0x02
  DIR = 0x04
  LINK = 0x08
  DEVICE = 0x10
  SOCKET = 0x20
  ANY = FILE | DIR | LINK | DEVICE
  FILE_OR_LINK = FILE | LINK
  FILE_OR_DIR = FILE | DIR
  FILE_OR_DIR_OR_LINK = FILE | DIR | LINK

  def mask_matches(self, mask):
    return (self & mask) != 0
  
bf_file_type.register_check_class()

class bf_cli_file_type(bcli_type_checked_enum):
  __enum_class__ = bf_file_type
