#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_command_handler import cli_command_handler
from ..system.check import check

from .xattr_exe import xattr_exe

class xattr_exe_cli_handler(cli_command_handler):
  'xattr_exe cli handler.'

  def __init__(self, cli_args):
    super(xattr_exe_cli_handler, self).__init__(cli_args)

  def keys(self, filename):
    check.check_string(filename)

    keys = xattr_exe.keys(filename)
    for key in keys:
      print(key)
    return 0
