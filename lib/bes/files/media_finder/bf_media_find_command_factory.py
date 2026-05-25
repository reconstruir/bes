#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

class bf_media_find_command_factory(bcli_command_factory_base):

  @classmethod
  #@abstractmethod
  def path(clazz):
    return 'media'

  @classmethod
  #@abstractmethod
  def description(clazz):
    return 'Find and inspect media files'

  #@abstractmethod
  def error_class(self):
    from bes.files.core.bf_error import bf_error
    return bf_error

  #@abstractmethod
  def options_class(self):
    from .bf_media_find_cli_options import bf_media_find_cli_options
    return bf_media_find_cli_options

  #@abstractmethod
  def has_commands(self):
    return True

  #@abstractmethod
  def add_commands(self, subparsers):
    default_media_types = self.default('media_types')
    default_sort_type   = self.default('sort_type')
    default_ignore_file = self.default('ignore_file')

    p = subparsers.add_parser('find', help='Find media files.')
    p.add_argument('where', action='store', nargs='+',
                   help='One or more root directories to search.')
    p.add_argument('--media-type', '-m', dest='media_types', action='store',
                   default=default_media_types,
                   choices=['image', 'video', 'all'],
                   help='Media types to include [ all ]')
    p.add_argument('--sort', '-s', dest='sort_type', action='store',
                   default=default_sort_type,
                   choices=['found_order', 'name', 'path', 'date', 'size', 'kind'],
                   help='Sort order for results [ found_order ]')
    p.add_argument('--ignore-file', dest='ignore_file', action='store',
                   default=default_ignore_file,
                   help='Per-directory ignore filename [ .bes_ignore ]; pass "" to disable')
    p.add_argument('--case-sensitive', dest='case_sensitive', action='store_true',
                   default=False,
                   help='Make string sorts (name, path, kind) case-sensitive')
    p.add_argument('--verbose', '-v', action='store_true', default=False,
                   help='Print filenames as found during scan')
    p.add_argument('--count', action='store_true', default=False,
                   help='Print only the final count, not filenames')

  #@abstractmethod
  def add_arguments(self, parser):
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Debug mode')

  #@abstractmethod
  def handler_class(self):
    from .bf_media_find_command_handler import bf_media_find_command_handler
    return bf_media_find_command_handler

  #@abstractmethod
  def supported_platforms(self):
    return 'all'
