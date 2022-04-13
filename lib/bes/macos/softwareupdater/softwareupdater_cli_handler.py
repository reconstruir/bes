#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.cli.cli_command_handler import cli_command_handler
from ..system.check import check

from .softwareupdater import softwareupdater
from .softwareupdater_options import softwareupdater_options

from bes.macos.command_line_tools.command_line_tools_force import command_line_tools_force

class softwareupdater_cli_handler(cli_command_handler):

  def __init__(self, cli_args):
    super(softwareupdater_cli_handler, self).__init__(cli_args, options_class = softwareupdater_options)
    check.check_softwareupdater_options(self.options)
    self._softwareupdater = softwareupdater(self.options)
  
  def available(self, force_command_line_tools):
    with command_line_tools_force(force = force_command_line_tools) as force:
      items = self._softwareupdater.available()
      for item in items:
        print('{} - {} - {}'.format(item.label, item.version, item.size))
      return 0

  def install(self, label, verbose):
    check.check_string(label)

    self._softwareupdater.install(label, verbose)
    return 0
