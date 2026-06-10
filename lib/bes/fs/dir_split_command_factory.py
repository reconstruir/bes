#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

from .dir_split_command_handler import dir_split_command_handler
from .dir_split_defaults import dir_split_defaults
from .dir_split_options import dir_split_options

class dir_split_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'dir_split'

  @classmethod
  def description(clazz):
    return 'Split a directory into many directories'

  def error_class(self):
    raise RuntimeError

  def options_class(self):
    return dir_split_options

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    parser.add_argument('--dry-run', action='store_true', default=False,
                        dest='dry_run',
                        help='Do not do anything, just print what would happen [ False ]')
    parser.add_argument('-r', '--recursive', action='store_true', default=False,
                        help='Split directories recursively [ False ]')
    parser.add_argument('--verbose', action='store_true', default=False,
                        help='Verbose output [ False ]')
    parser.add_argument('--chunk-size', action='store', type=int,
                        default=dir_split_defaults.CHUNK_SIZE,
                        dest='chunk_size',
                        help=f'Number of files per split directory [ {dir_split_defaults.CHUNK_SIZE} ]')
    parser.add_argument('--prefix', action='store', type=str,
                        default=dir_split_defaults.PREFIX,
                        help=f'Prefix for the split directory names [ {dir_split_defaults.PREFIX} ]')
    parser.add_argument('--sort', action='store',
                        default=dir_split_defaults.SORT_ORDER,
                        dest='sort_order',
                        help=f'How to sort files before splitting [ {dir_split_defaults.SORT_ORDER} ]')
    parser.add_argument('--reverse', action='store_true',
                        default=dir_split_defaults.SORT_REVERSE,
                        dest='sort_reverse',
                        help='Whether to reverse the file order after sorting [ False ]')
    parser.add_argument('--threshold', action='store', default=dir_split_defaults.THRESHOLD,
                        type=int,
                        dest='threshold',
                        help='Threshold of files needed to split a directory [ None ]')

  def add_commands(self, subparsers):
    p = subparsers.add_parser('split', help='Split a directory into many directories.')
    p.add_argument('src_dir', action='store', type=str, default=None,
                   help='The source directory [ None ]')
    p.add_argument('--dst-dir', action='store', type=str, default=None,
                   dest='dst_dir',
                   help='The destination directory [ None ]')

  def handler_class(self):
    return dir_split_command_handler

  def supported_platforms(self):
    return 'all'
