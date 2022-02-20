#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class file_split_cli_args(object):

  def __init__(self):
    pass
  
  def file_split_add_args(self, subparser):
    # unsplit
    p = subparser.add_parser('unsplit', help = 'Unsplit files.')
    self.__file_split_cli_add_add_common_args(p)
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files or dirs to find dups in [ None ]')
    
  @classmethod
  def __file_split_cli_add_add_common_args(clazz, p):
    p.add_argument('--dry-run', action = 'store_true', default = False,
                   help = 'Dont do anything just print what would happen [ None ]')
    p.add_argument('-r', '--recursive', action = 'store_true', default = False,
                   help = 'Find dups recursively [ None ]')
    p.add_argument('--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('--downloading', action = 'store_true', default = False,
                   dest = 'check_downloading',
                   help = 'Check if files are still downloading [ False ]')
    p.add_argument('--downloading-ext', action = 'store', default = 'part',
                   type = str, dest = 'check_downloading_extension',
                   help = 'Extension to check for downloding files [ False ]')
    p.add_argument('--ignore-ext', action = 'append', dest = 'ignore_extensions', default = [],
                   help = 'Ignore these extenstions when appened to the split files.')
    p.add_argument('--unzip', action = 'store_true', default = False,
                   help = 'If the unsplit file is an archive, then unzip it [ False ]')
    
  def _command_file_split(self, command, *args, **kargs):
    from .file_split_cli_handler import file_split_cli_handler
    return file_split_cli_handler(kargs).handle_command(command)
