#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

class softwareupdater_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'softwareupdater'

  @classmethod
  def description(clazz):
    return 'Manage macOS software updates'

  def error_class(self):
    from .softwareupdater_error import softwareupdater_error
    raise softwareupdater_error

  def options_class(self):
    from .softwareupdater_command_options import softwareupdater_command_options
    return softwareupdater_command_options

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Verbose output [ False ]')
    parser.add_argument('--sudo-password', action='store', default=None,
                        dest='sudo_password',
                        help='Sudo password [ None ]')

  def add_commands(self, subparsers):
    p = subparsers.add_parser('available', help='Print available updates.')
    p.add_argument('-f', '--force-command-line-tools', action='store_true', default=False,
                   dest='force_command_line_tools',
                   help='Force the command line tools to be available [ False ]')

    p = subparsers.add_parser('install', help='Install an item by label.')
    p.add_argument('label', action='store', default=None,
                   help='Label of the item to install [ None ]')

  def handler_class(self):
    from .softwareupdater_command_handler import softwareupdater_command_handler
    return softwareupdater_command_handler

  def supported_platforms(self):
    return 'darwin'
