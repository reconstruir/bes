#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

from . import uv_installer_command_handler
from . import uv_installer_command_options
from . import uv_installer_error

class uv_installer_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'uv_installer'

  @classmethod
  def description(clazz):
    return 'Install and manage the uv package manager'

  def error_class(self):
    return uv_installer_error.uv_installer_error

  def options_class(self):
    return uv_installer_command_options.uv_installer_command_options

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Verbose output [ False ]')
    parser.add_argument('--dry-run', action='store_true', default=False,
                        dest='dry_run',
                        help='Do not perform any changes [ False ]')
    parser.add_argument('--install-dir', action='store', default=None,
                        dest='install_dir',
                        help='Override the default install directory [ None ]')
    parser.add_argument('--install-script', action='store', default=None,
                        dest='install_script',
                        help='Path to a local install script for offline use [ None ]')
    parser.add_argument('--version', action='store', default=None,
                        dest='version',
                        help='Pin to a specific uv version [ latest ]')

  def add_commands(self, subparsers):
    p = subparsers.add_parser('install', help='Install uv.')
    p.add_argument('version', action='store', nargs='?', default=None,
                   help='The version of uv to install [ latest ]')

    subparsers.add_parser('uninstall', help='Uninstall uv.')

    subparsers.add_parser('is_installed', help='Check if uv is installed.')

    subparsers.add_parser('installed_version', help='Print the installed uv version.')

    subparsers.add_parser('exe_path', help='Print the path to the uv binary.')

  def handler_class(self):
    return uv_installer_command_handler.uv_installer_command_handler

  def supported_platforms(self):
    return 'all'
