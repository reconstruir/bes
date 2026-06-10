#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

class properties_file_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'properties_file'

  @classmethod
  def description(clazz):
    return 'Manage properties files'

  def error_class(self):
    raise RuntimeError

  def options_class(self):
    from .properties_file_command_options import properties_file_command_options
    return properties_file_command_options

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Verbose output [ False ]')

  def add_commands(self, subparsers):
    p = subparsers.add_parser('set', help='Set a property in a property file.')
    p.add_argument('filename', action='store', default=None, type=str,
                   help='The property filename [ None ]')
    p.add_argument('key', action='store', default=None, type=str,
                   help='The property key [ None ]')
    p.add_argument('value', action='store', default=None, type=str,
                   help='The property value [ None ]')

    p = subparsers.add_parser('get', help='Get a property from a property file.')
    p.add_argument('filename', action='store', default=None, type=str,
                   help='The property filename [ None ]')
    p.add_argument('key', action='store', default=None, type=str,
                   help='The property key [ None ]')

    p = subparsers.add_parser('bump_version', help='Bump a property version.')
    p.add_argument('filename', action='store', default=None, type=str,
                   help='The property filename [ None ]')
    p.add_argument('key', action='store', default=None, type=str,
                   help='The property key [ None ]')
    p.add_argument('-c', '--component', action='store', default='revision', type=str,
                   choices=['major', 'minor', 'revision'],
                   help='Which version component to bump [ revision ]')

    p = subparsers.add_parser('change_version', help='Change a property version.')
    p.add_argument('filename', action='store', default=None, type=str,
                   help='The property filename [ None ]')
    p.add_argument('key', action='store', default=None, type=str,
                   help='The property key [ None ]')
    p.add_argument('component', action='store', default='revision', type=str,
                   choices=['major', 'minor', 'revision'],
                   help='Which version component to change [ None ]')
    p.add_argument('value', action='store', default=None, type=str,
                   help='The new value [ None ]')

  def handler_class(self):
    from .properties_file_command_handler import properties_file_command_handler
    return properties_file_command_handler

  def supported_platforms(self):
    return 'all'
