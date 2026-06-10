#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

class pip_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'pip'

  @classmethod
  def description(clazz):
    return 'Inspect and manage pip executables'

  def error_class(self):
    from .pip_error import pip_error
    raise pip_error

  def options_class(self):
    from .pip_command_options import pip_command_options
    return pip_command_options

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Verbose output [ False ]')

  def add_commands(self, subparsers):
    p = subparsers.add_parser('ver', help='Print pip version.')
    p.add_argument('pip_exe', action='store', type=str, default=None,
                   help='The pip executable [ None ]')

    p = subparsers.add_parser('info', help='Print pip info.')
    p.add_argument('pip_exe', action='store', type=str, default=None,
                   help='The pip executable [ None ]')

    p = subparsers.add_parser('filename_info', help='Print pip filename info.')
    p.add_argument('pip_exe', action='store', type=str, default=None,
                   help='The pip executable [ None ]')

    p = subparsers.add_parser('exe_for_python', help='Find pip executable for a specific python exe.')
    p.add_argument('python_exe', action='store', type=str, default=None,
                   help='The python executable [ None ]')

  def handler_class(self):
    from .pip_command_handler import pip_command_handler
    return pip_command_handler

  def supported_platforms(self):
    return 'all'
