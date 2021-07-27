#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.cli.argparser_handler import argparser_handler
from bes.common.check import check
from bes.cli.cli_command_handler import cli_command_handler

from .sudo import sudo
from .sudo_cli_options import sudo_cli_options

class sudo_cli_handler(cli_command_handler):

  def __init__(self, cli_args):
    super(sudo_cli_handler, self).__init__(cli_args, options_class = sudo_cli_options)
    check.check_sudo_cli_options(self.options)
  
  def run(self, cmd):
    check.check_string_seq(cmd)

    sudo.call_sudo(cmd, self.options)
    return 0

  def authenticate(self):
    sudo.authenticate(self.options)
    return 0

  def is_authenticated(self):
    if sudo.is_authenticated(self.options):
      return 0
    else:
      return 1

  def reset(self):
    sudo.reset(self.options)
    return 0
  
