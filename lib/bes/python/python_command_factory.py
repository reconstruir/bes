#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

class python_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'python'

  @classmethod
  def description(clazz):
    return 'Inspect and manage python executables'

  def error_class(self):
    raise RuntimeError

  def options_class(self):
    from .python_command_options import python_command_options
    return python_command_options

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Verbose output [ False ]')

  def add_commands(self, subparsers):
    subparsers.add_parser('ver', help='Print the python sys.version.')

    subparsers.add_parser('path', help='Print the python sys.path.')

    p = subparsers.add_parser('info', help='Print information about the python executable.')
    p.add_argument('exe', action='store',
                   help='The python executable')

    p = subparsers.add_parser('exes', help='Print all the pythons found in PATH.')
    p.add_argument('-i', '--info', action='store_true', dest='show_info',
                   default=False, help='Print info about the executable')

    subparsers.add_parser('default_exe', help='Print the default python exe.')

  def handler_class(self):
    from .python_command_handler import python_command_handler
    return python_command_handler

  def supported_platforms(self):
    return 'all'
