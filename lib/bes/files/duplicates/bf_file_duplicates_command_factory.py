#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_i import bcli_command_factory_i

class bf_file_duplicates_command_factory(bcli_command_factory_i):

  @classmethod
  #@abstractmethod
  def path(clazz):
    return 'files/dups'

  @classmethod
  #@abstractmethod
  def description(clazz):
    return 'Resolve files and directories'
  
  #@abstractmethod
  def error_class(self):
    from .bf_file_duplicates_error import bf_file_duplicates_error
    raise bf_file_duplicates_error

  #@abstractmethod
  def options_class(self):
    from .bf_file_duplicates_cli_options import bf_file_duplicates_cli_options
    return bf_file_duplicates_cli_options
  
  #@abstractmethod
  def has_commands(self):
    return True
  
  #@abstractmethod
  def add_commands(self, subparsers):
    p = subparsers.add_parser('find', help = 'Find duplictes in these files and/or directions.')
    p.add_argument('--name', action = 'store', default = None,
                   help = 'Name to resolve [ None ]')
    p.add_argument('--type', '-t', dest = 'file_type', action = 'store', default = 'FILE_OR_LINK',
                   help = 'Type if file to resolve [ None ]')
    p.add_argument('--mindepth', action = 'store', dest = 'min_depth', default = None, type = int,
                   help = 'Min depth [ None ]')
    p.add_argument('--maxdepth', action = 'store', dest = 'max_depth', default = None, type = int,
                   help = 'Max depth [ None ]')
    p.add_argument('--quiet', '-q', action = 'store_true', default = False,
                   help = 'Run quietly.  Do not print out filenames [ False ]')
    p.add_argument('--stop-at', action = 'store', default = None, type = int,
                   help = 'Stop after resolving the given number of matches. [ None ]')
    p.add_argument('where', action = 'store', default = [], nargs = '+',
                   help = 'A mix of files and dirs where to resolve files.')
    
    '''
    from .bf_file_duplicates_defaults import bf_file_duplicates_defaults
    p = subparser.add_parser('dups', help = 'Find dups in files or directories.')
    self.__file_duplicates_cli_add_add_common_args(p)
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files or dirs to find dups in [ None ]')
    p.add_argument('--delete', action = 'store_true', default = False,
                   help = 'Delete the duplicates [ False ]')
    p.add_argument('--empty', action = 'store_true',
                   default = bf_file_duplicates_defaults.INCLUDE_EMPTY_FILES,
                   dest = 'include_empty_files',
                   help = 'Include empty files [ False ]')
    p.add_argument('--keep', action = 'store_true', default = False,
                   dest = 'keep_empty_dirs',
                   help = 'Keep empty directories after deleting dups [ False ]')
    p.add_argument('--small-checksum-size', action = 'store',
                   default = bf_file_duplicates_defaults.SMALL_CHECKSUM_SIZE,
                   help = f'Small checksum [ {bf_file_duplicates_defaults.SMALL_CHECKSUM_SIZE} ]')
    p.add_argument('--prefer', action = 'append', dest = 'prefer_prefixes', default = [],
                   help = 'Prefer the files starting at the given prefix.')
    p.add_argument('--ignore', action = 'append', dest = 'ignore_files', default = [],
                   help = 'Ignore file.')
    p.add_argument('--delete-empty-dirs', action = 'store_true',
                   default = bf_file_duplicates_defaults.DELETE_EMPTY_DIRS,
                   help = 'Delete empty directories after partitioning [ False ]')
'''    
  #@abstractmethod
  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action = 'store_true',
                        default = False, help = 'Verbose output')
    parser.add_argument('--debug', action = 'store_true',
                        default = False, help = 'Debug mode')

  #@abstractmethod
  def handler_class(self):
    from .bf_file_duplicates_command_handler import bf_file_duplicates_command_handler
    return bf_file_duplicates_command_handler

  #@abstractmethod
  def supported_platforms(self):
    return 'all'
