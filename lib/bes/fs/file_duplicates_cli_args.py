#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class file_duplicates_cli_args(object):

  def __init__(self):
    pass
  
  def file_duplicates_add_args(self, subparser):
    # dups
    from .file_duplicates_defaults import file_duplicates_defaults
    p = subparser.add_parser('dups', help = 'Find dups in files or directories.')
    self.__file_duplicates_cli_add_add_common_args(p)
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files or dirs to find dups in [ None ]')
    p.add_argument('--delete', action = 'store_true', default = False,
                   help = 'Delete the duplicates [ False ]')
    p.add_argument('--empty', action = 'store_true',
                   default = file_duplicates_defaults.INCLUDE_EMPTY_FILES,
                   dest = 'include_empty_files',
                   help = 'Include empty files [ False ]')
    p.add_argument('--keep', action = 'store_true', default = False,
                   dest = 'keep_empty_dirs',
                   help = 'Keep empty directories after deleting dups [ False ]')
    p.add_argument('--small-checksum-size', action = 'store',
                   default = file_duplicates_defaults.SMALL_CHECKSUM_SIZE,
                   help = f'Small checksum [ {file_duplicates_defaults.SMALL_CHECKSUM_SIZE} ]')
    p.add_argument('--prefer', action = 'append', dest = 'prefer_prefixes', default = [],
                   help = 'Prefer the files starting at the given prefix.')
    p.add_argument('--ignore', action = 'append', dest = 'ignore_files', default = [],
                   help = 'Ignore file.')
    p.add_argument('--delete-empty-dirs', action = 'store_true',
                   default = file_duplicates_defaults.DELETE_EMPTY_DIRS,
                   help = 'Delete empty directories after partitioning [ False ]')
    
  @classmethod
  def __file_duplicates_cli_add_add_common_args(clazz, p):
    p.add_argument('--dry-run', action = 'store_true', default = False,
                   help = 'Dont do anything just print what would happen [ None ]')
    p.add_argument('-r', '--recursive', action = 'store_true', default = False,
                   help = 'Find dups recursively [ None ]')
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('--quiet', action = 'store_true', default = False,
                   help = 'Quiet output [ False ]')
    
  def _command_file_duplicates(self, command, *args, **kargs):
    from .file_duplicates_cli_handler import file_duplicates_cli_handler
    return file_duplicates_cli_handler(kargs).handle_command(command)
