#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

from .dir_partition_command_handler import dir_partition_command_handler
from .dir_partition_defaults import dir_partition_defaults
from .dir_partition_options import dir_partition_options

class dir_partition_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'dir_partition'

  @classmethod
  def description(clazz):
    return 'Partition a directory into many directories'

  def error_class(self):
    raise RuntimeError

  def options_class(self):
    return dir_partition_options

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    parser.add_argument('--dry-run', action='store_true', default=False,
                        dest='dry_run',
                        help='Do not do anything, just print what would happen [ False ]')
    parser.add_argument('-r', '--recursive', action='store_true', default=False,
                        help='Partition directories recursively [ False ]')
    parser.add_argument('--verbose', action='store_true', default=False,
                        help='Verbose output [ False ]')
    parser.add_argument('--type', action='store',
                        default=dir_partition_defaults.PARTITION_TYPE,
                        dest='partition_type',
                        help=f'Partition type to use [ {dir_partition_defaults.PARTITION_TYPE} ]')
    parser.add_argument('-d', '--dst-dir', action='store',
                        default=dir_partition_defaults.DST_DIR,
                        dest='dst_dir',
                        help='Destination directory [ cwd ]')
    parser.add_argument('--threshold', action='store',
                        default=dir_partition_defaults.THRESHOLD,
                        type=int,
                        dest='threshold',
                        help='Threshold of files needed to partition a directory [ None ]')
    parser.add_argument('--delete-empty-dirs', action='store_true',
                        default=dir_partition_defaults.DELETE_EMPTY_DIRS,
                        dest='delete_empty_dirs',
                        help='Delete empty directories after partitioning [ False ]')
    parser.add_argument('--flatten', action='store_true',
                        default=dir_partition_defaults.FLATTEN,
                        help=f'Flatten directory hierarchies [ {dir_partition_defaults.FLATTEN} ]')

  def add_commands(self, subparsers):
    p = subparsers.add_parser('partition',
                              help='Partition a directory into many directories.')
    p.add_argument('files', nargs='+',
                   help='One or more files or dirs to partition')

  def handler_class(self):
    return dir_partition_command_handler

  def supported_platforms(self):
    return 'all'
