#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check

from .brew import brew
from .brew_options import brew_options

class brew_cli_handler(cli_command_handler):

  def __init__(self, cli_args):
    super(brew_cli_handler, self).__init__(cli_args,
                                           options_class = brew_options)
    check.check_brew_options(self.options)
  
  def info(self):
    version = brew.version()
    print('version: {}'.format(version))
    return 0
