#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class dir_cli_args(object):

  def __init__(self):
    pass
  
  def dir_add_args(self, subparser):

    # split
    p = subparser.add_parser('split', help = 'Split a directory into many directories.')
    p.add_argument('src_dir', action = 'store', type = str, default = None,
                   help = 'The source directory [ None ]')
    p.add_argument('dst_dir', action = 'store', type = str, default = None,
                   help = 'The destination directory [ None ]')
    p.add_argument('chunk_size', action = 'store', type = int, default = None,
                   help = 'The chunk size for the split directories [ None ]')
    p.add_argument('--prefix', action = 'store', type = str, default = 'split-',
                   help = 'Prefix for the split directory names [ None ]')
    p.add_argument('--dry-run', action = 'store_true', default = False,
                   help = 'Dont do anything just print what would happen [ None ]')
    p.add_argument('--recursive', action = 'store_true', default = False,
                   help = 'Split directories recursively [ None ]')
     
  def _command_dir(self, command, *args, **kargs):
    from .dir_cli_handler import dir_cli_handler
    return dir_cli_handler(kargs).handle_command(command)
