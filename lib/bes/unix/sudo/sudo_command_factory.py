#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

class sudo_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'sudo'

  @classmethod
  def description(clazz):
    return 'Run commands with sudo and manage sudo authentication'

  def error_class(self):
    raise RuntimeError

  def options_class(self):
    from .sudo_command_options import sudo_command_options
    return sudo_command_options

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Verbose output [ False ]')
    parser.add_argument('--password', action='store', default=None,
                        help='The sudo password to use [ ]')
    parser.add_argument('--prompt', action='store', default=None,
                        help='The sudo prompt to use [ ]')
    parser.add_argument('--working-dir', action='store', default=None,
                        dest='working_dir',
                        help='The working directory [ ]')

  def add_commands(self, subparsers):
    p = subparsers.add_parser('run', help='Run a command with sudo.')
    p.add_argument('cmd', action='store', default=None, nargs='+',
                   help='Command to run [ ]')

    p = subparsers.add_parser('authenticate', help='Authenticate with sudo.')
    p.add_argument('--force', action='store_true', default=False,
                   dest='force_auth',
                   help='Force auth even if already authenticated [ False ]')

    subparsers.add_parser('is_authenticated', help='Return 0 if authenticated 1 otherwise.')

    subparsers.add_parser('reset', help='Reset authentication.')

  def handler_class(self):
    from .sudo_command_handler import sudo_command_handler
    return sudo_command_handler

  def supported_platforms(self):
    return 'all'
