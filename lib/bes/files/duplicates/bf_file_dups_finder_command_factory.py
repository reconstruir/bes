#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_i import bcli_command_factory_i

class bf_file_dups_finder_command_factory(bcli_command_factory_i):

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
    from .bf_file_dups_finder_error import bf_file_dups_finder_error
    raise bf_file_dups_finder_error

  #@abstractmethod
  def options_class(self):
    from .bf_file_dups_finder_cli_options import bf_file_dups_finder_cli_options
    return bf_file_dups_finder_cli_options
  
  #@abstractmethod
  def has_commands(self):
    return True
  
  #@abstractmethod
  def add_commands(self, subparsers):
    include_empty_files = self.default('include_empty_files')
    delete_empty_dirs = self.default('delete_empty_dirs')
    include_hard_links = self.default('include_hard_links')
    include_soft_links = self.default('include_soft_links')
    
    p = subparsers.add_parser('find', help = 'Find duplictes in these files and/or directions.')
    p.add_argument('where', action = 'store', default = [], nargs = '+',
                   help = 'A mix of files and dirs where to resolve files.')
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
    p.add_argument('--include-empty-files', action = 'store_true',
                   default = include_empty_files,
                   help = f'Include empty files [ {include_empty_files} ]')
    p.add_argument('--include-hard-links', action = 'store_true',
                   default = include_hard_links,
                   help = f'Include hard links [ {include_hard_links} ]')
    p.add_argument('--include-soft-links', action = 'store_true',
                   default = include_soft_links,
                   help = f'Include soft links [ {include_soft_links} ]')
    p.add_argument('--delete-empty-dirs', action = 'store_true',
                   default = delete_empty_dirs,
                   help = f'Delete empty dirs [ {delete_empty_dirs} ]')

    '''

    self.__file_duplicates_cli_add_add_common_args(p)
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files or dirs to find dups in [ None ]')
    p.add_argument('--keep', action = 'store_true', default = False,
                   dest = 'keep_empty_dirs',
                   help = 'Keep empty directories after deleting dups [ False ]')
    p.add_argument('--prefer', action = 'append', dest = 'prefer_prefixes', default = [],
                   help = 'Prefer the files starting at the given prefix.')
    p.add_argument('--ignore', action = 'append', dest = 'ignore_files', default = [],
                   help = 'Ignore file.')
'''    
  #@abstractmethod
  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action = 'store_true',
                        default = False, help = 'Verbose output')
    parser.add_argument('--debug', action = 'store_true',
                        default = False, help = 'Debug mode')

  #@abstractmethod
  def handler_class(self):
    from .bf_file_dups_finder_command_handler import bf_file_dups_finder_command_handler
    return bf_file_dups_finder_command_handler

  #@abstractmethod
  def supported_platforms(self):
    return 'all'
