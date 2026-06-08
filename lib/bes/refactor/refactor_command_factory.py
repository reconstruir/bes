#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

class refactor_command_factory(bcli_command_factory_base):

  @classmethod
  #@abstractmethod
  def path(clazz):
    return 'refactor'

  @classmethod
  #@abstractmethod
  def description(clazz):
    return 'Refactor python code'

  #@abstractmethod
  def error_class(self):
    from .refactor_error import refactor_error
    return refactor_error

  #@abstractmethod
  def options_class(self):
    from .refactor_cli_options import refactor_cli_options
    return refactor_cli_options

  #@abstractmethod
  def has_commands(self):
    return True

  #@abstractmethod
  def add_commands(self, subparsers):
    p = subparsers.add_parser('rename', help = 'Global rename of dirs, files and content.')
    p.add_argument('src_pattern', action = 'store', default = None,
                   help = 'The src pattern to rename from [ ]')
    p.add_argument('dst_pattern', action = 'store', default = None,
                   help = 'The dst pattern to rename to [ ]')
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files and/or directories to rename [ ]')

    p = subparsers.add_parser('copy', help = 'Global copy of files and content.')
    p.add_argument('src_pattern', action = 'store', default = None,
                   help = 'The src pattern to copy from [ ]')
    p.add_argument('dst_pattern', action = 'store', default = None,
                   help = 'The dst pattern to copy to [ ]')
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files and/or directories to copy [ ]')
    p.add_argument('--dirs', action = 'store_true', default = False,
                   dest = 'copy_dirs',
                   help = 'Copy dirs as well if needed [ False ]')

    p = subparsers.add_parser('rename_dirs', help = 'Global rename of dirs only.')
    p.add_argument('src_pattern', action = 'store', default = None,
                   help = 'The src pattern to rename from [ ]')
    p.add_argument('dst_pattern', action = 'store', default = None,
                   help = 'The dst pattern to rename to [ ]')
    p.add_argument('dirs', action = 'store', default = [], nargs = '+',
                   help = 'One or more directories to rename [ ]')

    p = subparsers.add_parser('rename_files', help = 'Global rename of files only.')
    p.add_argument('src_pattern', action = 'store', default = None,
                   help = 'The src pattern to rename from [ ]')
    p.add_argument('dst_pattern', action = 'store', default = None,
                   help = 'The dst pattern to rename to [ ]')
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files and/or directories to rename [ ]')

    p = subparsers.add_parser('replace_text', help = 'Global search and replace of text in files.')
    p.add_argument('src_pattern', action = 'store', default = None,
                   help = 'The src pattern to replace [ ]')
    p.add_argument('dst_pattern', action = 'store', default = None,
                   help = 'The dst pattern to replace with [ ]')
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files and/or directories to replace text in [ ]')

    p = subparsers.add_parser('reindent', help = 'Global reindent of python code.')
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files and/or directories to reindent [ ]')
    p.add_argument('-i', '--indent', action = 'store', default = 2, type = int,
                   help = 'Indent depth [ 2 ]')

    from .refactor_ast_node_type import refactor_ast_node_type
    p = subparsers.add_parser('grep', help = 'Grep python code taking into account structure.')
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files and/or directories to grep [ ]')
    p.add_argument('text', action = 'store', default = None, type = str,
                   help = 'Text to grep for [ ]')
    p.add_argument('-t', '--type', action = 'store', default = refactor_ast_node_type.FUNCTION,
                   dest = 'node_type', choices = refactor_ast_node_type.values,
                   help = 'The type of node to grep [ FUNCTION ]')

    p = subparsers.add_parser('function_add_arg', help = 'Add an argument to all matching functions.')
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files and/or directories [ ]')
    p.add_argument('function_name', action = 'store', default = None, type = str,
                   help = 'The function name [ ]')
    p.add_argument('arg_name', action = 'store', default = None, type = str,
                   help = 'The arg name [ ]')

  #@abstractmethod
  def add_arguments(self, parser):
    parser.add_argument('--dry-run', action = 'store_true', default = False,
                        dest = 'dry_run',
                        help = 'Dont do anything just print what would happen [ False ]')
    parser.add_argument('-v', '--verbose', action = 'store_true', default = False,
                        help = 'Verbose output [ False ]')
    parser.add_argument('-w', '--word-boundary', action = 'store_true', default = False,
                        dest = 'word_boundary',
                        help = 'Respect word boundaries [ False ]')
    parser.add_argument('-d', '--debug', action = 'store_true', default = False,
                        help = 'Debug mode [ False ]')
    parser.add_argument('-g', '--git', action = 'store_true', default = False,
                        dest = 'try_git',
                        help = 'Use git to move or add files [ False ]')
    parser.add_argument('--unsafe', action = 'store_true', default = False,
                        help = 'Ignore unsafe operations like clobbering existing files [ False ]')
    parser.add_argument('--backup', action = 'store_true', default = False,
                        help = 'Make backups for reindented files [ False ]')

  #@abstractmethod
  def handler_class(self):
    from .refactor_command_handler import refactor_command_handler
    return refactor_command_handler

  #@abstractmethod
  def supported_platforms(self):
    return 'all'
