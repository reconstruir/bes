#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

from .bf_checksum_algorithm import bf_checksum_algorithm

class bf_checksum_command_factory(bcli_command_factory_base):

  @classmethod
  #@abstractmethod
  def path(clazz):
    return 'files/checksum'

  @classmethod
  #@abstractmethod
  def description(clazz):
    return 'Compute and print file checksums'

  #@abstractmethod
  def error_class(self):
    from .bf_checksum_error import bf_checksum_error
    raise bf_checksum_error

  #@abstractmethod
  def options_class(self):
    from .bf_checksum_command_options import bf_checksum_command_options
    return bf_checksum_command_options

  #@abstractmethod
  def has_commands(self):
    return True

  #@abstractmethod
  def add_commands(self, subparsers):
    default_algorithm = self.default('algorithm')

    p = subparsers.add_parser('print', help = 'Print checksums for resolved files.')
    p.add_argument('where', action = 'store', default = [], nargs = '+',
                   help = 'A mix of files and dirs where to resolve files.')
    p.add_argument('--algorithm', '-a', action = 'store', default = default_algorithm,
                   choices = bf_checksum_algorithm.ALL,
                   help = f'Checksum algorithm to use [ {default_algorithm} ]')

  #@abstractmethod
  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action = 'store_true',
                        default = False, help = 'Verbose output')
    parser.add_argument('--debug', action = 'store_true',
                        default = False, help = 'Debug mode')

  #@abstractmethod
  def handler_class(self):
    from .bf_checksum_command_handler import bf_checksum_command_handler
    return bf_checksum_command_handler

  #@abstractmethod
  def supported_platforms(self):
    return 'all'
