#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class dir_split_cli_args(object):

  def __init__(self):
    pass
  
  def dir_split_add_args(self, subparser):
    # split
    from .dir_split_defaults import dir_split_defaults
    p = subparser.add_parser('split', help = 'Split a directory into many directories.')
    self.__dir_split_cli_add_add_common_args(p)
    p.add_argument('src_dir', action = 'store', type = str, default = None,
                   help = 'The source directory [ None ]')
    p.add_argument('--dst-dir', action = 'store', type = str, default = None,
                   help = 'The destination directory [ None ]')
    p.add_argument('--chunk-size', action = 'store', type = str,
                   default = dir_split_defaults.CHUNK_SIZE,
                   help = 'Prefix for the split directory names [ None ]')
    p.add_argument('--prefix', action = 'store', type = str,
                   default = dir_split_defaults.PREFIX,
                   help = 'Prefix for the split directory names [ None ]')
    p.add_argument('--sort', action = 'store',
                   default = dir_split_defaults.SORT_ORDER, dest = 'sort_order',
                   help = 'How to sort files before splitting [ None ]')
    p.add_argument('--reverse', action = 'store_true',
                   default = dir_split_defaults.SORT_REVERSE, dest = 'sort_reverse',
                   help = 'Whether to reverse the file order after sorting [ None ]')
    p.add_argument('--threshold', action = 'store',
                   default = dir_split_defaults.THRESHOLD,
                   type = int,
                   help = 'Threshold of files needed to split a directory [ None ]')
    
  @classmethod
  def __dir_split_cli_add_add_common_args(clazz, p):
    p.add_argument('--dry-run', action = 'store_true', default = False,
                   help = 'Dont do anything just print what would happen [ None ]')
    p.add_argument('-r', '--recursive', action = 'store_true', default = False,
                   help = 'Split directories recursively [ None ]')
    p.add_argument('--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    
  def _command_dir_split(self, command, *args, **kargs):
    from .dir_split_cli_handler import dir_split_cli_handler
    return dir_split_cli_handler(kargs).handle_command(command)
