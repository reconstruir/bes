#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

class native_package_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'native_package'

  @classmethod
  def description(clazz):
    return 'Manage native system packages'

  def error_class(self):
    from .native_package_error import native_package_error
    raise native_package_error

  def options_class(self):
    from .native_package_command_options import native_package_command_options
    return native_package_command_options

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Verbose output [ False ]')
    parser.add_argument('--sudo-password', action='store', default=None,
                        dest='sudo_password',
                        help='Sudo password [ None ]')

  def add_commands(self, subparsers):
    subparsers.add_parser('list', help='List installed packages.')

    p = subparsers.add_parser('installed', help='Check if package_name is installed.')
    p.add_argument('package_name', action='store', help='The package name')

    p = subparsers.add_parser('info', help='Print platform specific info about package.')
    p.add_argument('package_name', action='store', help='The package name')

    p = subparsers.add_parser('files', help='Print package files.')
    p.add_argument('package_name', action='store', help='The package name')
    p.add_argument('--levels', '-l', action='store', type=int, default=None,
                   help='Show only top level directories [ None ]')

    p = subparsers.add_parser('dirs', help='Print package dirs.')
    p.add_argument('package_name', action='store', help='The package name')
    p.add_argument('--levels', '-l', action='store', type=int, default=None,
                   help='Show only top level directories [ None ]')
    p.add_argument('--root-dir', action='store_true', default=False,
                   dest='root_dir',
                   help='Show only the root dir [ False ]')

    p = subparsers.add_parser('owner', help='Print the package that owns the given file.')
    p.add_argument('filename', action='store', help='The filename')

    p = subparsers.add_parser('remove', help='Remove a package.')
    p.add_argument('package_name', action='store', help='The package name')
    p.add_argument('--force-package-root', action='store_true', default=False,
                   dest='force_package_root',
                   help='Force removal of the package root directory [ False ]')

    p = subparsers.add_parser('install', help='Install a package.')
    p.add_argument('package_filename', action='store', help='The package file')

  def handler_class(self):
    from .native_package_command_handler import native_package_command_handler
    return native_package_command_handler

  def supported_platforms(self):
    return 'all'
