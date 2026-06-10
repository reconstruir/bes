#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

class system_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'system'

  @classmethod
  def description(clazz):
    return 'System utilities (processes, open files)'

  def error_class(self):
    raise RuntimeError

  def options_class(self):
    from .system_command_options import system_command_options
    return system_command_options

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Verbose output [ False ]')

  def add_commands(self, subparsers):
    subparsers.add_parser('ps', help='List processes.')

    p = subparsers.add_parser('lsof', help='List open file descriptors for a process.')
    p.add_argument('pid', action='store', type=int, default=None,
                   help='The process id [ ]')

  def handler_class(self):
    from .system_command_handler import system_command_handler
    return system_command_handler

  def supported_platforms(self):
    return 'all'
