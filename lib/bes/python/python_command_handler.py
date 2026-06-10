#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.system.check import check
from bes.text.text_table import text_table

from .python_exe import python_exe

class python_command_handler(bcli_command_handler):

  def name(self):
    return 'python'

  def _command_ver(self, options):
    print(sys.version)
    return 0

  def _command_path(self, options):
    for p in sys.path:
      print(p)
    return 0

  def _command_info(self, exe, options):
    python_exe.check_exe(exe)

    info = python_exe.info(exe)
    data = [item for item in zip(tuple(info._fields), info)]
    tt = text_table(data=data)
    print(tt)
    return 0

  def _command_exes(self, show_info, options):
    check.check_bool(show_info)

    python_exes = python_exe.find_all_exes()
    for exe in python_exes:
      print(exe)
      if show_info:
        self._command_info(exe, options)
    return 0

  def _command_default_exe(self, options):
    exe = python_exe.default_exe()
    if not exe:
      print('')
      return 1
    print(exe)
    return 0
