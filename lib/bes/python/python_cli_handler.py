#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys

from bes.cli.cli_command_handler import cli_command_handler
from ..system.check import check
from bes.text.text_table import text_table

from .python_exe import python_exe

class python_cli_handler(cli_command_handler):
  'python cli handler.'

  def __init__(self, cli_args):
    super(python_cli_handler, self).__init__(cli_args)
  
  def ver(self):
    print(sys.version)
    return 0

  def path(self):
    for p in sys.path:
      print(p)
    return 0

  def info(self, exe):
    python_exe.check_exe(exe)

    info = python_exe.info(exe)
    data = [ item for item in zip(tuple(info._fields), info) ]
    tt = text_table(data = data)
    print(tt)
    return 0

  def exes(self, show_info):
    check.check_bool(show_info)
    
    python_exes = python_exe.find_all_exes()
    for exe in python_exes:
      print(exe)
      if show_info:
        self.info(exe)
    return 0

  def default_exe(self):
    exe = python_exe.default_exe()
    if not exe:
      print('')
      return 1
    print(exe)
    return 0
