#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import dataclasses

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
  
  @property
  def want_file(self):
    return self.mask_matches(self.FILE)

  @property
  def want_dir(self):
    return self.mask_matches(self.DIR)

  @property
  def want_link(self):
    return self.mask_matches(self.LINK)

  @property
  def want_device(self):
    return self.mask_matches(self.DEVICE)

  @property
  def want_socket(self):
    return self.mask_matches(self.SOCKET)
  
bf_file_type.register_check_class()

class bf_cli_file_type(bcli_type_checked_enum):
  __enum_class__ = bf_file_type
