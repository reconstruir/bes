#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class files_cli_args(object):

  def __init__(self):
    pass
  
  def files_add_args(self, subparser):
    # dup_basenames
    p = subparser.add_parser('dup_basenames', help = 'Find duplicate basenames.')
    self.__files_cli_add_add_common_args(p)
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files or dirs to check for dup basenames [ None ]')
    
    # checksums
    p = subparser.add_parser('checksums', help = 'Print checksums for files.')
    self.__files_cli_add_add_common_args(p)
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files or dirs to print checksums for [ None ]')
    p.add_argument('-a', '--algorithm', action = 'store', default = 'sha256',
                   choices = ( 'md5', 'sha1', 'sha256' ),
                   help = 'The checksum algorithm to use [ sha256 ]')

    # media_types
    p = subparser.add_parser('media_types', help = 'Print media types for files.')
    self.__files_cli_add_add_common_args(p)
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files or dirs to print media types for [ None ]')

    # mime_types
    p = subparser.add_parser('mime_types', help = 'Print mime types for files.')
    self.__files_cli_add_add_common_args(p)
    p.add_argument('--cached', action = 'store_true', default = False,
                   help = 'Use the value cached in file attributes if present [ False ]')
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files or dirs to print mime types for [ None ]')
    
    # hexify
    p = subparser.add_parser('hexify', help = 'Hexify a binary such that it can be included in python code.')
    self.__files_cli_add_add_common_args(p)
    p.add_argument('filename', action = 'store', type = str, default = None,
                   help = 'The filename [ None ]')

    # check_access 
    p = subparser.add_parser('check_access', help = 'Check access for files.')
    self.__files_cli_add_add_common_args(p)
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files or dirs to check access for [ None ]')
    p.add_argument('-l', '--level', action = 'append', default = [ 'write' ],
                   choices = ( 'exists', 'read', 'write', 'execute' ),
                   dest = 'levels',
                   help = 'The level of access to check for [ write ]')

    # resolve
    p = subparser.add_parser('resolve', help = 'Resolve a mixture of files and directories into just files.')
    self.__files_cli_add_add_common_args(p)
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files or dirs to resolve [ None ]')

    # prefixes
    p = subparser.add_parser('prefixes', help = 'Print all detected prefixes for files.')
    self.__files_cli_add_add_common_args(p)
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files or dirs to detect prefixes for [ None ]')

    # cat
    p = subparser.add_parser('cat', help = 'Concatenate a bunch of files.')
    self.__files_cli_add_add_common_args(p)
    p.add_argument('--sort', action = 'store_true', default = False,
                   help = 'Sort the files semantically first [ False ]')
    p.add_argument('-o', '--output-filename', action = 'store', default = None,
                   help = 'The output filename [ None ]')
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files or dirs to concatenate [ None ]')

    # move
    p = subparser.add_parser('move', help = 'Move files from one dir hierarchy to another without clobbering dup filenames.')
    self.__files_cli_add_add_common_args(p)
    p.add_argument('src_dir', action = 'store', default = None,
                   help = 'The src directory [ None ]')
    p.add_argument('dst_dir', action = 'store', default = None,
                   help = 'The dst directory [ None ]')

    # delete
    p = subparser.add_parser('delete', help = 'Delete files or diretories.')
    self.__files_cli_add_add_common_args(p)
    p.add_argument('--from-file', action = 'store', default = None,
                   help = 'Read list of files to delete from a file [ None ]')
    p.add_argument('files', action = 'store', default = [], nargs = '*',
                   help = 'One or more files or dirs to print mime types for [ None ]')
    
  @classmethod
  def __files_cli_add_add_common_args(clazz, p):
    p.add_argument('--dry-run', action = 'store_true', default = False,
                   help = 'Dont do anything just print what would happen [ None ]')
    p.add_argument('-r', '--recursive', action = 'store_true', default = False,
                   help = 'Find files recursively [ False ]')
    p.add_argument('--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('--ignore', action = 'append', dest = 'ignore_files', default = [],
                   help = 'Ignore file.')
    p.add_argument('--dup-file-timestamp', action = 'store', default = None,
                   help = 'Timestamp for resolving duplicate files [ None ]')
    p.add_argument('--dup-file-count', action = 'store', default = None, type = int,
                   help = 'Count to begin at for resolving duplicate files [ 1 ]')
    
  def _command_files(self, command, *args, **kargs):
    from .files_cli_handler import files_cli_handler
    return files_cli_handler(kargs).handle_command(command)
