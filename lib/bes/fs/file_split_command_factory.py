#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

from .file_split_command_handler import file_split_command_handler
from .file_split_options import file_split_options

class file_split_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'file_split'

  @classmethod
  def description(clazz):
    return 'Find and unsplit split files'

  def error_class(self):
    raise RuntimeError

  def options_class(self):
    return file_split_options

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    parser.add_argument('--dry-run', action='store_true', default=False,
                        dest='dry_run',
                        help='Do not do anything, just print what would happen [ False ]')
    parser.add_argument('-r', '--recursive', action='store_true', default=False,
                        help='Find files recursively [ False ]')
    parser.add_argument('--verbose', action='store_true', default=False,
                        help='Verbose output [ False ]')
    parser.add_argument('--downloading', action='store_true', default=False,
                        dest='check_downloading',
                        help='Check if files are still downloading [ False ]')
    parser.add_argument('--downloading-ext', action='store', default='part',
                        type=str, dest='check_downloading_extension',
                        help='Extension to check for downloading files [ part ]')
    parser.add_argument('--ignore-ext', action='append', dest='ignore_extensions', default=[],
                        help='Ignore these extensions when appended to the split files')
    parser.add_argument('--unzip', action='store_true', default=False,
                        help='If the unsplit file is an archive, then unzip it [ False ]')
    parser.add_argument('--ignore-incomplete', action='store_true', default=False,
                        dest='ignore_incomplete',
                        help='Ignore incomplete sets instead of raising errors [ False ]')

  def add_commands(self, subparsers):
    p = subparsers.add_parser('unsplit', help='Unsplit files.')
    p.add_argument('files', nargs='+',
                   help='One or more files or dirs to find split files in')

  def handler_class(self):
    return file_split_command_handler

  def supported_platforms(self):
    return 'all'
