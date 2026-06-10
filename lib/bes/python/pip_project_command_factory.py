#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

class pip_project_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'pip_project'

  @classmethod
  def description(clazz):
    return 'Manage pip virtual environment projects'

  def error_class(self):
    from .pip_error import pip_error
    raise pip_error

  def options_class(self):
    from .pip_project_command_options import pip_project_command_options
    return pip_project_command_options

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Verbose output [ False ]')
    parser.add_argument('-r', '--root-dir', action='store', default=None,
                        dest='root_dir',
                        help='The root directory where to install pip [ None ]')
    parser.add_argument('--python-version', action='store', default=None,
                        dest='python_version',
                        help='The python version to use [ None ]')
    parser.add_argument('--python-exe', action='store', default=None,
                        dest='python_exe',
                        help='The python exe to use [ None ]')
    parser.add_argument('--output', action='store', default=None,
                        dest='output_filename',
                        help='Optional output filename [ None ]')
    parser.add_argument('--style', action='store', default='table',
                        dest='output_style',
                        help='Output style [ table ]')
    parser.add_argument('--limit', action='store', default=None,
                        dest='limit_num_items',
                        help='Limit the number of response items shown [ None ]')

  def add_commands(self, subparsers):
    subparsers.add_parser('create', help='Create a pip project.')

    p = subparsers.add_parser('install', help='Install a package.')
    p.add_argument('package_name', action='store', type=str, default=None,
                   help='The name of the package to install [ None ]')
    p.add_argument('--version', action='store', type=str, default=None,
                   help='Optional package version [ latest ]')

    p = subparsers.add_parser('upgrade', help='Upgrade a package.')
    p.add_argument('packages', action='store', default=[], nargs='+',
                   help='The name of the packages to upgrade [ None ]')

    p = subparsers.add_parser('install_requirements', help='Install packages from a requirements file.')
    p.add_argument('requirements_files', action='store', default=[], nargs='+',
                   help='One or more requirements files [ None ]')

    subparsers.add_parser('outdated', help='Print outdated packages.')

    subparsers.add_parser('installed', help='Print installed packages.')

    p = subparsers.add_parser('pip', help='Run pip command.')
    p.add_argument('args', action='store', default=[], nargs='+',
                   help='The pip args [ None ]')

    p = subparsers.add_parser('activate_script', help='Print the activate script for the virtual env.')
    p.add_argument('--variant', action='store', type=str, default=None,
                   help='The virtual env variant (csh, fish, ps1) [ None ]')

    p = subparsers.add_parser('version', help='Print version of a package.')
    p.add_argument('package_name', action='store', type=str, default=None,
                   help='The name of the package [ None ]')

  def handler_class(self):
    from .pip_project_command_handler import pip_project_command_handler
    return pip_project_command_handler

  def supported_platforms(self):
    return 'all'
