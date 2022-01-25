#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class file_split_cli_args(object):

  def __init__(self):
    pass
  
  def file_split_add_args(self, subparser):
    # dups
    p = subparser.add_parser('dups', help = 'Find dups in files or directories.')
    self.__file_split_cli_add_add_common_args(p)
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files or dirs to find dups in [ None ]')
    p.add_argument('--delete', action = 'store_true', default = False,
                   help = 'Delete the duplicates [ False ]')
    p.add_argument('--empty', action = 'store_true', default = False,
                   dest = 'include_empty_files',
                   help = 'Include empty files [ False ]')
    p.add_argument('--keep', action = 'store_true', default = False,
                   dest = 'keep_empty_dirs',
                   help = 'Keep empty directories after removing dups [ False ]')
    default_small_checksum_size = 1024 * 1024
    p.add_argument('--small-checksum-size', action = 'store', default = default_small_checksum_size,
                   help = f'Small checksum [ {default_small_checksum_size} ]')
    
  @classmethod
  def __file_split_cli_add_add_common_args(clazz, p):
    p.add_argument('--dry-run', action = 'store_true', default = False,
                   help = 'Dont do anything just print what would happen [ None ]')
    p.add_argument('-r', '--recursive', action = 'store_true', default = False,
                   help = 'Find dups recursively [ None ]')
    p.add_argument('--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    
  def _command_file_split(self, command, *args, **kargs):
    from .file_split_cli_handler import file_split_cli_handler
    return file_split_cli_handler(kargs).handle_command(command)
