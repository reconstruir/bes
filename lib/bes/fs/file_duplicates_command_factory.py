#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

from .file_duplicates_command_handler import file_duplicates_command_handler
from .file_duplicates_defaults import file_duplicates_defaults
from .file_duplicates_options import file_duplicates_options

class file_duplicates_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'file_duplicates'

  @classmethod
  def description(clazz):
    return 'Find and manage duplicate files'

  def error_class(self):
    raise RuntimeError

  def options_class(self):
    return file_duplicates_options

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    parser.add_argument('--dry-run', action='store_true', default=False,
                        dest='dry_run',
                        help='Do not do anything, just print what would happen [ False ]')
    parser.add_argument('-r', '--recursive', action='store_true', default=False,
                        help='Find dups recursively [ False ]')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Verbose output [ False ]')
    parser.add_argument('--quiet', action='store_true', default=False,
                        help='Quiet output [ False ]')
    parser.add_argument('--small-checksum-size', action='store',
                        default=file_duplicates_defaults.SMALL_CHECKSUM_SIZE,
                        dest='small_checksum_size',
                        help=f'Small checksum size [ {file_duplicates_defaults.SMALL_CHECKSUM_SIZE} ]')
    parser.add_argument('--prefer', action='append', dest='prefer_prefixes', default=[],
                        help='Prefer files starting with the given prefix')
    parser.add_argument('--ignore', action='append', dest='ignore_files', default=[],
                        help='Ignore file')
    parser.add_argument('--empty', action='store_true',
                        default=file_duplicates_defaults.INCLUDE_EMPTY_FILES,
                        dest='include_empty_files',
                        help=f'Include empty files [ {file_duplicates_defaults.INCLUDE_EMPTY_FILES} ]')
    parser.add_argument('--delete-empty-dirs', action='store_true',
                        default=file_duplicates_defaults.DELETE_EMPTY_DIRS,
                        dest='delete_empty_dirs',
                        help='Delete empty directories after deleting dups [ False ]')

  def add_commands(self, subparsers):
    p = subparsers.add_parser('dups', help='Find dups in files or directories.')
    p.add_argument('files', nargs='+',
                   help='One or more files or dirs to find dups in')
    p.add_argument('--delete', action='store_true', default=False,
                   help='Delete the duplicates [ False ]')
    p.add_argument('--keep', action='store_true', default=False,
                   dest='keep_empty_dirs',
                   help='Keep empty directories after deleting dups [ False ]')

  def handler_class(self):
    return file_duplicates_command_handler

  def supported_platforms(self):
    return 'all'
