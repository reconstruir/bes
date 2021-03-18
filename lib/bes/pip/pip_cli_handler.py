#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import sys

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check
from bes.common.Script import Script
from bes.script.blurber import blurber

from .pip_error import pip_error
from .pip_exe import pip_exe
from .pip_options import pip_options

class pip_cli_handler(cli_command_handler):
  'pip cli handler.'

  def __init__(self, cli_args):
    super(pip_cli_handler, self).__init__(cli_args, options_class = pip_options)
    check.check_pip_options(self.options)
    self.options.blurber.set_verbose(self.options.verbose)
    
  def ver(self, py_exe):
    check.check_string(py_exe)
    
    exe = pip_exe.pip_exe(py_exe)
    print(pip_exe.version(exe))
    return 0

  def info(self, py_exe):
    check.check_string(py_exe)

    exe = pip_exe.pip_exe(py_exe)
    print(pip_exe.version_info(exe))
    return 0

  def present(self, py_exe):
    check.check_string(py_exe)

    exe = pip_exe.pip_exe(py_exe)
    print('exe={}'.format(exe))
    if pip_exe.pip_exe_is_valid(exe):
      return 0
    else:
      return 1
