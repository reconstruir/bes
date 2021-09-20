#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check

from .shell_framework import shell_framework
from .shell_framework_options import shell_framework_options

from bes.macos.command_line_tools.command_line_tools_force import command_line_tools_force

class shell_framework_cli_handler(cli_command_handler):

  def __init__(self, cli_args):
    super(shell_framework_cli_handler, self).__init__(cli_args, options_class = shell_framework_options)
    check.check_shell_framework_options(self.options)
    self._shell_framework = shell_framework(self.options)
  
  def latest(self):
    print(self._shell_framework.latest_revision)
    return 0

  def update(self):
    self._shell_framework.update()
    return 0
