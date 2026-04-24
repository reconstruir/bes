#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

class bf_metadata_command_factory(bcli_command_factory_base):

  @classmethod
  #@abstractmethod
  def path(clazz):
    return 'files/metadata'

  @classmethod
  #@abstractmethod
  def description(clazz):
    return 'Read and write file metadata stored in SQLite'

  #@abstractmethod
  def error_class(self):
    from .bf_metadata_error import bf_metadata_error
    raise bf_metadata_error

  #@abstractmethod
  def options_class(self):
    from .bf_metadata_command_options import bf_metadata_command_options
    return bf_metadata_command_options

  #@abstractmethod
  def has_commands(self):
    return True

  #@abstractmethod
  def add_commands(self, subparsers):
    p = subparsers.add_parser('list', help = 'List all metadata key/value pairs for a file.')
    p.add_argument('filename', action = 'store',
                   help = 'File to inspect.')

    p = subparsers.add_parser('clear', help = 'Delete all metadata for a file.')
    p.add_argument('filename', action = 'store',
                   help = 'File whose metadata to clear.')
    p.add_argument('--yes', '-y', action = 'store_true', default = False,
                   help = 'Skip confirmation prompt.')

    p = subparsers.add_parser('set', help = 'Set a metadata key/value pair for a file.')
    p.add_argument('key', action = 'store',
                   help = 'Metadata key.')
    p.add_argument('value', action = 'store',
                   help = 'Metadata value.')
    p.add_argument('filename', action = 'store',
                   help = 'File to update.')

    p = subparsers.add_parser('get', help = 'Get a metadata value for a file.')
    p.add_argument('key', action = 'store',
                   help = 'Metadata key.')
    p.add_argument('filename', action = 'store',
                   help = 'File to inspect.')

    p = subparsers.add_parser('keys', help = 'List all metadata keys for a file.')
    p.add_argument('filename', action = 'store',
                   help = 'File to inspect.')

  #@abstractmethod
  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action = 'store_true',
                        default = False, help = 'Verbose output')
    parser.add_argument('--debug', action = 'store_true',
                        default = False, help = 'Debug mode')

  #@abstractmethod
  def handler_class(self):
    from .bf_metadata_command_handler import bf_metadata_command_handler
    return bf_metadata_command_handler

  #@abstractmethod
  def supported_platforms(self):
    return 'all'
