#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

class archive_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'archive'

  @classmethod
  def description(clazz):
    return 'Manage archives'

  def error_class(self):
    raise RuntimeError

  def options_class(self):
    from .archive_command_options import archive_command_options
    return archive_command_options

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Verbose output [ False ]')

  def add_commands(self, subparsers):
    p = subparsers.add_parser('remove_members', help='Remove members from the archive.')
    p.add_argument('archive', action='store', default=None,
                   help='The archive filename [ None ]')
    p.add_argument('members', action='store', default=None, nargs='+',
                   help='The members to remove [ None ]')

    p = subparsers.add_parser('contents', help='Show the contents of an archive.')
    p.add_argument('archives', action='store', default=[], nargs='+',
                   help='Archives to show contents of [ ]')

    p = subparsers.add_parser('duplicates', help='Show duplicates between archives contents.')
    p.add_argument('--check-content', action='store_true', default=False,
                   dest='check_content',
                   help='Check content checksums [ False ]')
    p.add_argument('archives', action='store', default=[], nargs='+',
                   help='Archives to check for duplicates [ ]')

    default_dest_dir = os.getcwd()
    p = subparsers.add_parser('extract', help='Extract archives.')
    p.add_argument('--dest-dir', action='store', default=default_dest_dir,
                   dest='dest_dir',
                   help='Destination dir [ {} ]'.format(default_dest_dir))
    p.add_argument('archives', action='store', default=[], nargs='+',
                   help='Archives to extract [ ]')

    p = subparsers.add_parser('extract_file', help='Extract a file from an archive.')
    p.add_argument('archive_filename', action='store', default=None,
                   help='The archive [ None ]')
    p.add_argument('filename', action='store', default=None,
                   help='The filename to extract [ None ]')
    p.add_argument('-o', '--output-filename', action='store', default=None,
                   dest='output_filename',
                   help='The output filename [ None ]')

    p = subparsers.add_parser('cat', help='Cat a member file.')
    p.add_argument('archive_filename', action='store', default=None,
                   help='The archive [ None ]')
    p.add_argument('filename', action='store', default=None,
                   help='The filename to extract [ None ]')

    p = subparsers.add_parser('combine', help='Combine archives.')
    p.add_argument('dest_archive', action='store', default=None,
                   help='The destination archive [ ]')
    p.add_argument('archives', action='store', default=[], nargs='+',
                   help='Archives to combine [ ]')
    p.add_argument('--check-content', action='store_true', default=False,
                   dest='check_content',
                   help='Check content checksums [ False ]')
    p.add_argument('--base-dir', action='store', default=None,
                   dest='base_dir',
                   help='Use this base dir for dest_archive [ None ]')
    p.add_argument('--exclude', action='append', default=[],
                   dest='exclude',
                   help='Exclude the given member [ ]')

    p = subparsers.add_parser('diff', help='Diff content of 2 archives.')
    p.add_argument('archive1', action='store', default=None,
                   help='The first archive [ ]')
    p.add_argument('archive2', action='store', default=None,
                   help='The second archive [ ]')

    p = subparsers.add_parser('diff_manifest', help='Diff the manifest of 2 archives.')
    p.add_argument('archive1', action='store', default=None,
                   help='The first archive [ ]')
    p.add_argument('archive2', action='store', default=None,
                   help='The second archive [ ]')

    p = subparsers.add_parser('diff_dir', help='Diff content of a dir of archives.')
    p.add_argument('dir1', action='store', default=None,
                   help='The first dir [ ]')
    p.add_argument('dir2', action='store', default=None,
                   help='The second dir [ ]')

    p = subparsers.add_parser('search', help='Search for text in the archives contents.')
    p.add_argument('archive', action='store', default=None,
                   help='The archive [ ]')
    p.add_argument('text', action='store', default=None,
                   help='The text to search for [ ]')
    p.add_argument('-i', '--ignore-case', action='store_true', default=False,
                   dest='ignore_case',
                   help='Ignore case [ False ]')
    p.add_argument('-w', '--whole-word', action='store_true', default=False,
                   dest='whole_word',
                   help='Only match whole words [ False ]')

  def handler_class(self):
    from .archive_command_handler import archive_command_handler
    return archive_command_handler

  def supported_platforms(self):
    return 'all'
