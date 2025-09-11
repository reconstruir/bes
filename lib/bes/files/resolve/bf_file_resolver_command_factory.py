#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

class bf_file_resolver_command_factory(bcli_command_factory_base):

  @classmethod
  #@abstractmethod
  def path(clazz):
    return 'resolve'

  @classmethod
  #@abstractmethod
  def description(clazz):
    return 'Resolve files and directories'
  
  #@abstractmethod
  def error_class(self):
    from .bf_file_resolver_error import bf_file_resolver_error
    raise bf_file_resolver_error

  #@abstractmethod
  def options_class(self):
    from .bf_file_resolver_cli_options import bf_file_resolver_cli_options
    return bf_file_resolver_cli_options
  
  #@abstractmethod
  def has_commands(self):
    return True
  
  #@abstractmethod
  def add_commands(self, subparsers):
    default_file_type = self.default('file_type')
    default_sort_order = self.default('sort_order')
    
    p = subparsers.add_parser('files', help = 'Resolve files.')
    p.add_argument('--name', action = 'store', default = None,
                   help = 'Name to resolve [ None ]')
    p.add_argument('--type', '-t', dest = 'file_type', action = 'store',
                   default = default_file_type, choices = default_file_type.choices,
                   help = 'Type if file to resolve [ None ]')
    p.add_argument('--sort', '-s', dest = 'sort_order', action = 'store',
                   default = default_sort_order, choices = default_sort_order.choices,
                   help = f'Sort order for resulting resolved files [ {default_sort_order.name} ]')
    p.add_argument('--mindepth', action = 'store', dest = 'min_depth',
                   default = None, type = int, 
                   help = 'Min depth [ None ]')
    p.add_argument('--maxdepth', action = 'store', dest = 'max_depth', default = None, type = int,
                   help = 'Max depth [ None ]')
    p.add_argument('--quiet', '-q', action = 'store_true', default = False,
                   help = 'Run quietly.  Do not print out filenames [ False ]')
    p.add_argument('--stop-at', action = 'store', default = None, type = int,
                   help = 'Stop after resolving the given number of matches. [ None ]')
    p.add_argument('where', action = 'store', default = [], nargs = '+',
                   help = 'A mix of files and dirs where to resolve files.')
    
  #@abstractmethod
  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action = 'store_true',
                        default = False, help = 'Verbose output')
    parser.add_argument('--debug', action = 'store_true',
                        default = False, help = 'Debug mode')

  #@abstractmethod
  def handler_class(self):
    from .bf_file_resolver_command_handler import bf_file_resolver_command_handler
    return bf_file_resolver_command_handler

  #@abstractmethod
  def supported_platforms(self):
    return 'all'
