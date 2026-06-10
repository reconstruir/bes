#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

class linux_attr_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'linux_attr'

  @classmethod
  def description(clazz):
    return 'Manage Linux extended attributes on files'

  def error_class(self):
    raise RuntimeError

  def options_class(self):
    from .linux_attr_command_options import linux_attr_command_options
    return linux_attr_command_options

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Verbose output [ False ]')

  def add_commands(self, subparsers):
    p = subparsers.add_parser('keys', help='Print keys for a file.')
    p.add_argument('filename', action='store', default=None,
                   help='The file [ None ]')

  def handler_class(self):
    from .linux_attr_command_handler import linux_attr_command_handler
    return linux_attr_command_handler

  def supported_platforms(self):
    return 'linux'
