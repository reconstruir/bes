#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

class python_installer_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'python_installer'

  @classmethod
  def description(clazz):
    return 'Install and manage python versions'

  def error_class(self):
    raise RuntimeError

  def options_class(self):
    from .python_installer_command_options import python_installer_command_options
    return python_installer_command_options

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Verbose output [ False ]')
    parser.add_argument('--installer', action='store', default=None, type=str,
                        dest='installer_name',
                        help='The installer to use [ None ]')
    parser.add_argument('--system', action='store', default=None, type=str,
                        choices=('linux', 'macos', 'windows'),
                        help='The target system [ None ]')
    parser.add_argument('--dry-run', action='store_true', default=False,
                        dest='dry_run',
                        help='Do not do any work, just print what would happen [ False ]')
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Debug mode [ False ]')

  def add_commands(self, subparsers):
    subparsers.add_parser('installed', help='Return the full versions for all installed pythons.')

    p = subparsers.add_parser('is_installed', help='Check if python is installed.')
    p.add_argument('version', action='store',
                   help='The version of python to check')

    p = subparsers.add_parser('install', help='Install python.')
    p.add_argument('version', action='store',
                   help='The version of python to install')

    p = subparsers.add_parser('update', help='Update python.')
    p.add_argument('version', action='store',
                   help='The version of python to update')

    p = subparsers.add_parser('needs_update', help='Check if python version needs update.')
    p.add_argument('version', action='store',
                   help='The version of python to check for update')

    p = subparsers.add_parser('install_package', help='Install a python package file directly.')
    p.add_argument('package_filename', action='store',
                   help='The package filename')

    p = subparsers.add_parser('uninstall', help='Uninstall python.')
    p.add_argument('version', action='store',
                   help='The version of python to uninstall')

    p = subparsers.add_parser('reinstall', help='Reinstall python.')
    p.add_argument('version', action='store',
                   help='The version of python to reinstall')

    p = subparsers.add_parser('available', help='List python versions available to install.')
    p.add_argument('-n', '--num', action='store', type=int, default=3,
                   help='Number of versions to show for each major python version [ 3 ]')

    subparsers.add_parser('installers', help='List all available installers.')

    p = subparsers.add_parser('download', help='Download python package.')
    p.add_argument('full_version', action='store',
                   help='The full version of python to download')
    p.add_argument('-o', '--output', action='store', default=None,
                   dest='output_filename',
                   help='Output to filename instead of stdout [ None ]')

  def handler_class(self):
    from .python_installer_command_handler import python_installer_command_handler
    return python_installer_command_handler

  def supported_platforms(self):
    return 'all'
