#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import sys

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check
from bes.common.Script import Script
from bes.script.blurber import blurber
from bes.text.text_table import text_table

from .pip_error import pip_error
from .pip_exe import pip_exe as bes_pip_exe
from .pip_options import pip_options

class pip_cli_handler(cli_command_handler):
  'pip cli handler.'

  def __init__(self, cli_args):
    super(pip_cli_handler, self).__init__(cli_args, options_class = pip_options)
    check.check_pip_options(self.options)
    self.options.blurber.set_verbose(self.options.verbose)
    
  def ver(self, pip_exe):
    check.check_string(pip_exe)
    
    version = bes_pip_exe.version(pip_exe)
    print(version)
    return 0

  def info(self, pip_exe):
    check.check_string(pip_exe)

    info = bes_pip_exe.version_info(pip_exe)
    tt = text_table(data = zip(tuple(info._fields), info))
    print(tt)
    return 0

  def filename_info(self, pip_exe):
    check.check_string(pip_exe)

    info = bes_pip_exe.filename_info(pip_exe)
    tt = text_table(data = zip(tuple(info._fields), info))
    print(tt)
    return 0
