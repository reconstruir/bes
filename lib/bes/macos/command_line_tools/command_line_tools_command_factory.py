#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

from .command_line_tools_command_handler import command_line_tools_command_handler
from .command_line_tools_command_options import command_line_tools_command_options

class command_line_tools_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'command_line_tools'

  @classmethod
  def description(clazz):
    return 'Deal with command line tools'

  def error_class(self):
    raise RuntimeError

  def options_class(self):
    return command_line_tools_command_options

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action = 'store_true', default = False,
                        help = 'Verbose output [ False ]')

  def add_commands(self, subparsers):
    subparsers.add_parser('installed', help = 'Return 0 if command line tools are installed.')
    subparsers.add_parser('install', help = 'Install the command line tools.')
    subparsers.add_parser('ensure', help = 'Ensure the command line tools.')

  def handler_class(self):
    return command_line_tools_command_handler

  def supported_platforms(self):
    return 'darwin'
