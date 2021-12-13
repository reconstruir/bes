#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class files_cli_args(object):

  def __init__(self):
    pass
  
  def files_add_args(self, subparser):

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
    p.add_argument('--sort', action = 'store', default = 'filename',
                   dest = 'sort_order',
                   help = 'How to sort files before splitting [ None ]')
    p.add_argument('--reverse', action = 'store_true', default = False,
                   dest = 'sort_reverse',
                   help = 'Whether to reverse the file order after sorting [ None ]')

    # dups
    p = subparser.add_parser('dups', help = 'Find duplicate files in directories.')
    p.add_argument('dirs', action = 'store', default = [], nargs = '+',
                   help = 'One or more directories to check for dups [ None ]')
    p.add_argument('--delete', action = 'store_true', default = False,
                   help = 'Prefix for the split directory names [ None ]')
    p.add_argument('--dry-run', action = 'store_true', default = False,
                   help = 'Dont do anything just print what would happen [ None ]')
    p.add_argument('--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')

    # checksums
    p = subparser.add_parser('checksums', help = 'Print checksums for files.')
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more directories to check for dups [ None ]')
    p.add_argument('--dry-run', action = 'store_true', default = False,
                   help = 'Dont do anything just print what would happen [ None ]')
    p.add_argument('--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('-a', '--algorithm', action = 'store', default = 'sha256',
                   choices = ( 'md5', 'sha1', 'sha256' ),
                   help = 'The checksum algorithm to use [ sha256 ]')
    p.add_argument('--recursive', action = 'store_true', default = False,
                   help = 'Whether to recurse into subdirectories [ False ]')

    # media_types
    p = subparser.add_parser('media_types', help = 'Print media types for files.')
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more directories to check for dups [ None ]')
    p.add_argument('--dry-run', action = 'store_true', default = False,
                   help = 'Dont do anything just print what would happen [ None ]')
    p.add_argument('--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('--recursive', action = 'store_true', default = False,
                   help = 'Whether to recurse into subdirectories [ False ]')
    
    # remove_empty
    p = subparser.add_parser('remove_empty', help = 'Remove empty directories.')
    p.add_argument('where', action = 'store', type = str, default = None,
                   help = 'Where to start [ None ]')
    p.add_argument('--dry-run', action = 'store_true', default = False,
                   help = 'Dont do anything just print what would happen [ None ]')
    p.add_argument('--recursive', action = 'store_true', default = False,
                   help = 'Whether to recurse into subdirectories [ False ]')

    # hexify
    p = subparser.add_parser('hexify', help = 'Hexify a binary such that it can be included in python code.')
    p.add_argument('filename', action = 'store', type = str, default = None,
                   help = 'The filename [ None ]')
    
  def _command_files(self, command, *args, **kargs):
    from .files_cli_handler import files_cli_handler
    return files_cli_handler(kargs).handle_command(command)
