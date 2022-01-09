#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class refactor_cli_args(object):

  def __init__(self):
    pass
  
  def refactor_add_args(self, subparser):

    # rename
    p = subparser.add_parser('rename', help = 'Global rename of dirs, files and content.')
    self.__refactor_cli_add_add_common_args(p)
    p.add_argument('src_pattern', action = 'store', default = None,
                   help = 'The src pattern to rename from. []')
    p.add_argument('dst_pattern', action = 'store', default = None,
                   help = 'The dst pattern to rename to. []')
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files and/or directories to rename [ None ]')

    # clone
    p = subparser.add_parser('clone', help = 'Global clone of dirs, files and content.')
    self.__refactor_cli_add_add_common_args(p)
    p.add_argument('src_pattern', action = 'store', default = None,
                   help = 'The src pattern to clone from. []')
    p.add_argument('dst_pattern', action = 'store', default = None,
                   help = 'The dst pattern to clone to. []')
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files and/or directories to clone [ None ]')
    
    # rename_dirs
    p = subparser.add_parser('rename_dirs', help = 'Global rename of dirs only.')
    self.__refactor_cli_add_add_common_args(p)
    p.add_argument('src_pattern', action = 'store', default = None,
                   help = 'The src pattern to rename from. []')
    p.add_argument('dst_pattern', action = 'store', default = None,
                   help = 'The dst pattern to rename to. []')
    p.add_argument('dirs', action = 'store', default = [], nargs = '+',
                   help = 'One or more directories to rename [ None ]')

    # rename_files
    p = subparser.add_parser('rename_files', help = 'Global rename of files only.')
    self.__refactor_cli_add_add_common_args(p)
    p.add_argument('src_pattern', action = 'store', default = None,
                   help = 'The src pattern to rename from. []')
    p.add_argument('dst_pattern', action = 'store', default = None,
                   help = 'The dst pattern to rename to. []')
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more file and/or directories to rename [ None ]')

    # replace_text
    p = subparser.add_parser('replace_text', help = 'Global search and replace of text in files.')
    self.__refactor_cli_add_add_common_args(p)
    p.add_argument('src_pattern', action = 'store', default = None,
                   help = 'The src pattern to rename from. []')
    p.add_argument('dst_pattern', action = 'store', default = None,
                   help = 'The dst pattern to rename to. []')
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more file and/or directories to replace text in [ None ]')
    
  @classmethod
  def __refactor_cli_add_add_common_args(clazz, p):
    p.add_argument('--dry-run', action = 'store_true', default = False,
                   help = 'Dont do anything just print what would happen [ None ]')
    p.add_argument('--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('-w', '--word-boundary', action = 'store_true', default = False,
                   help = 'Respect word boundaries [ False ]')
    p.add_argument('-d', '--debug', action = 'store_true', default = False,
                   help = 'Debug mode [ False ]')
    p.add_argument('-g', '--git', action = 'store_true', default = False,
                   dest = 'try_git',
                   help = 'Use git to move or add files [ False ]')
    
  def _command_refactor(self, command, *args, **kargs):
    from .refactor_cli_handler import refactor_cli_handler
    return refactor_cli_handler(kargs).handle_command(command)
