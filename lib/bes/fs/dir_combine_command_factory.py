#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

from .dir_combine_command_handler import dir_combine_command_handler
from .dir_combine_defaults import dir_combine_defaults
from .dir_combine_options import dir_combine_options

class dir_combine_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'dir_combine'

  @classmethod
  def description(clazz):
    return 'Combine directories'

  def error_class(self):
    raise RuntimeError

  def options_class(self):
    return dir_combine_options

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    parser.add_argument('--dry-run', action='store_true', default=False,
                        dest='dry_run',
                        help='Do not do anything, just print what would happen [ False ]')
    parser.add_argument('-r', '--recursive', action='store_true', default=False,
                        help='Combine directories recursively [ False ]')
    parser.add_argument('--verbose', action='store_true', default=False,
                        help='Verbose output [ False ]')
    parser.add_argument('--dest-dir', action='store', default=None,
                        dest='destination_dir',
                        help='Destination directory [ None ]')
    parser.add_argument('--ignore-empty', action='store_true',
                        default=dir_combine_defaults.IGNORE_EMPTY,
                        dest='ignore_empty',
                        help=f'Ignore empty or non-existent directories [ {dir_combine_defaults.IGNORE_EMPTY} ]')
    parser.add_argument('--dup-file-timestamp', action='store', default=None,
                        dest='dup_file_timestamp',
                        help='Timestamp for resolving duplicate files [ None ]')
    parser.add_argument('--dup-file-count', action='store', type=int,
                        default=dir_combine_defaults.DUP_FILE_COUNT,
                        dest='dup_file_count',
                        help=f'Count to begin at for resolving duplicate files [ {dir_combine_defaults.DUP_FILE_COUNT} ]')
    parser.add_argument('--flatten', action='store_true',
                        default=dir_combine_defaults.FLATTEN,
                        help=f'Flatten directory hierarchies [ {dir_combine_defaults.FLATTEN} ]')
    parser.add_argument('--delete-empty-dirs', action='store_true',
                        default=dir_combine_defaults.DELETE_EMPTY_DIRS,
                        dest='delete_empty_dirs',
                        help=f'Delete empty directories after combining [ {dir_combine_defaults.DELETE_EMPTY_DIRS} ]')

  def add_commands(self, subparsers):
    p = subparsers.add_parser('combine',
                              help='Combine dirs and/or files into a single destination dir.')
    p.add_argument('files', nargs='+',
                   help='One or more files or dirs to combine')

  def handler_class(self):
    return dir_combine_command_handler

  def supported_platforms(self):
    return 'all'
