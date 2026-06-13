#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

from . import uv_error
from . import uv_project_command_handler
from . import uv_project_command_options

class uv_project_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'uv_project'

  @classmethod
  def description(clazz):
    return 'Manage uv virtual environment projects'

  def error_class(self):
    return uv_error.uv_error

  def options_class(self):
    return uv_project_command_options.uv_project_command_options

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Verbose output [ False ]')
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Debug output [ False ]')
    parser.add_argument('-r', '--root-dir', action='store', default=None,
                        dest='root_dir',
                        help='The root directory of the virtual environment [ None ]')
    parser.add_argument('--uv-exe', action='store', default=None,
                        dest='uv_exe',
                        help='Explicit path to the uv binary [ None ]')
    parser.add_argument('--python', action='store', default=None,
                        help='Python version or executable path for uv venv [ None ]')

  def add_commands(self, subparsers):
    subparsers.add_parser('create', help='Create the virtual environment.')

    p = subparsers.add_parser('install', help='Install a package.')
    p.add_argument('package_name', action='store', type=str,
                   help='The name of the package to install')
    p.add_argument('--version', action='store', type=str, default=None,
                   help='Optional package version [ latest ]')

    p = subparsers.add_parser('upgrade', help='Upgrade packages.')
    p.add_argument('packages', action='store', nargs='+',
                   help='Package names to upgrade')

    p = subparsers.add_parser('install_requirements', help='Install from requirements files.')
    p.add_argument('requirements_files', action='store', nargs='+',
                   help='One or more requirements files')

    subparsers.add_parser('installed', help='List installed packages.')

    subparsers.add_parser('outdated', help='List outdated packages.')

    p = subparsers.add_parser('version', help='Print version of an installed package.')
    p.add_argument('package_name', action='store', type=str,
                   help='The package name')

    subparsers.add_parser('exe_path', help='Print the path to the uv binary.')

  def handler_class(self):
    return uv_project_command_handler.uv_project_command_handler

  def supported_platforms(self):
    return 'all'
