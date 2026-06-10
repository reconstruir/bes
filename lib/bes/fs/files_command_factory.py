#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

from .files_cli_options import files_cli_options
from .files_command_handler import files_command_handler

class files_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'files'

  @classmethod
  def description(clazz):
    return 'File utilities'

  def error_class(self):
    raise RuntimeError

  def options_class(self):
    return files_cli_options

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
    parser.add_argument('--ignore', action='append', dest='ignore_files', default=[],
                        help='Ignore file [ None ]')
    parser.add_argument('--dup-file-timestamp', action='store', default=None,
                        dest='dup_file_timestamp',
                        help='Timestamp for resolving duplicate files [ None ]')
    parser.add_argument('--dup-file-count', action='store', default=1, type=int,
                        dest='dup_file_count',
                        help='Count to begin at for resolving duplicate files [ 1 ]')

  def add_commands(self, subparsers):
    p = subparsers.add_parser('checksums', help='Print checksums for files.')
    p.add_argument('files', nargs='+',
                   help='One or more files or dirs to print checksums for')
    p.add_argument('-a', '--algorithm', action='store', default='sha256',
                   choices=('md5', 'sha1', 'sha256'),
                   help='The checksum algorithm to use [ sha256 ]')

    p = subparsers.add_parser('media_types', help='Print media types for files.')
    p.add_argument('files', nargs='+',
                   help='One or more files or dirs to print media types for')

    p = subparsers.add_parser('mime_types', help='Print mime types for files.')
    p.add_argument('--cached', action='store_true', default=False,
                   help='Use the value cached in file attributes if present [ False ]')
    p.add_argument('files', nargs='+',
                   help='One or more files or dirs to print mime types for')

    p = subparsers.add_parser('hexify', help='Hexify a binary for inclusion in python code.')
    p.add_argument('filename', action='store', type=str, default=None,
                   help='The filename [ None ]')

    p = subparsers.add_parser('check_access', help='Check access for files.')
    p.add_argument('files', nargs='+',
                   help='One or more files or dirs to check access for')
    p.add_argument('-l', '--level', action='append', default=['write'],
                   choices=('exists', 'read', 'write', 'execute'),
                   dest='levels',
                   help='The level of access to check for [ write ]')

    p = subparsers.add_parser('resolve',
                              help='Resolve a mixture of files and directories into just files.')
    p.add_argument('files', nargs='+',
                   help='One or more files or dirs to resolve')

    p = subparsers.add_parser('prefixes', help='Print all detected prefixes for files.')
    p.add_argument('files', nargs='+',
                   help='One or more files or dirs to detect prefixes for')

    p = subparsers.add_parser('dup_basenames', help='Find duplicate basenames.')
    p.add_argument('files', nargs='+',
                   help='One or more files or dirs to check for dup basenames')

    p = subparsers.add_parser('cat', help='Concatenate a bunch of files.')
    p.add_argument('--sort', action='store_true', default=False,
                   help='Sort the files semantically first [ False ]')
    p.add_argument('-o', '--output-filename', action='store', default=None,
                   dest='output_filename',
                   help='The output filename [ None ]')
    p.add_argument('files', nargs='+',
                   help='One or more files or dirs to concatenate')

    p = subparsers.add_parser('move',
                              help='Move files from one dir hierarchy to another without clobbering dup filenames.')
    p.add_argument('src_dir', action='store', default=None,
                   help='The src directory [ None ]')
    p.add_argument('dst_dir', action='store', default=None,
                   help='The dst directory [ None ]')

    p = subparsers.add_parser('delete', help='Delete files or directories.')
    p.add_argument('--from-file', action='store', default=None,
                   dest='from_file',
                   help='Read list of files to delete from a file [ None ]')
    p.add_argument('files', nargs='*',
                   help='One or more files or dirs to delete')

  def handler_class(self):
    return files_command_handler

  def supported_platforms(self):
    return 'all'
