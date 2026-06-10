#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.system.check import check

from .xattr_exe import xattr_exe

class xattr_exe_command_handler(bcli_command_handler):

  def name(self):
    return 'xattr_exe'

  def _command_keys(self, filename, options):
    check.check_string(filename)

    keys = xattr_exe.keys(filename)
    for key in keys:
      print(key)
    return 0
