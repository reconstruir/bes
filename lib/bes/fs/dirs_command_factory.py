#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

class dirs_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'dirs'

  @classmethod
  def description(clazz):
    return 'Manage directories'

  def error_class(self):
    raise RuntimeError

  def options_class(self):
    from .dirs_command_options import dirs_command_options
    return dirs_command_options

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Verbose output [ False ]')

  def add_commands(self, subparsers):
    p = subparsers.add_parser('remove_empty', help='Remove empty directories.')
    p.add_argument('--dry-run', action='store_true', default=False,
                   dest='dry_run',
                   help='Do not do anything, just print what would happen [ False ]')
    p.add_argument('-r', '--recursive', action='store_true', default=False,
                   help='Find dirs recursively [ False ]')
    p.add_argument('where', action='store', type=str, default=None,
                   help='Root directory where to start looking for empty dirs [ None ]')

  def handler_class(self):
    from .dirs_command_handler import dirs_command_handler
    return dirs_command_handler

  def supported_platforms(self):
    return 'all'
