#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class dir_combine_cli_args(object):

  def __init__(self):
    pass
  
  def dir_combine_add_args(self, subparser):
    # combine
    from .dir_combine_defaults import dir_combine_defaults
    p = subparser.add_parser('combine', help = 'Combine dirs and/or files into a single destination dir.')
    self.__dir_combine_cli_add_add_common_args(p)
    p.add_argument('--dest-dir', action = 'store', default = None,
                   dest = 'destination_dir', help = 'Destination directory [ None ]')
    p.add_argument('--ignore-empty', action = 'store_true',
                   default = dir_combine_defaults.IGNORE_EMPTY,
                   help = f'Ignore empty or non-existent directories [ {dir_combine_defaults.IGNORE_EMPTY} ]')
    p.add_argument('--dup-file-timestamp', action = 'store',
                   default = dir_combine_defaults.DUP_FILE_TIMESTAMP,
                   help = f'Timestamp for resolving duplicate files [ {dir_combine_defaults.DUP_FILE_TIMESTAMP} ]')
    p.add_argument('--dup-file-count', action = 'store', type = int,
                   default = dir_combine_defaults.DUP_FILE_COUNT,
                   help = f'Count to begin at for resolving duplicate files [ {dir_combine_defaults.DUP_FILE_COUNT} ]')
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files or dirs to combine [ None ]')
    p.add_argument('--delete-empty-dirs', action = 'store_true',
                   default = dir_combine_defaults.DELETE_EMPTY_DIRS,
                   help = f'Delete empty directories after combining [ {dir_combine_defaults.DELETE_EMPTY_DIRS} ]')
    p.add_argument('--flatten', action = 'store_true',
                   default = dir_combine_defaults.FLATTEN,
                   help = f'Flatten directory hierachies [ {dir_combine_defaults.FLATTEN} ]')
    
  @classmethod
  def __dir_combine_cli_add_add_common_args(clazz, p):
    p.add_argument('--dry-run', action = 'store_true', default = False,
                   help = 'Dont do anything just print what would happen [ None ]')
    p.add_argument('-r', '--recursive', action = 'store_true', default = False,
                   help = 'Combine directories recursively [ None ]')
    p.add_argument('--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    
  def _command_dir_combine(self, command, *args, **kargs):
    from .dir_combine_cli_handler import dir_combine_cli_handler
    return dir_combine_cli_handler(kargs).handle_command(command)
