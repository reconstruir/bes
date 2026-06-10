#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

class bes_project_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'bes_project'

  @classmethod
  def description(clazz):
    return 'Manage bes python virtual environment projects'

  def error_class(self):
    from .bes_project_error import bes_project_error
    raise bes_project_error

  def options_class(self):
    from .bes_project_command_options import bes_project_command_options
    return bes_project_command_options

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Verbose output [ False ]')
    parser.add_argument('-r', '--root-dir', action='store', default=None,
                        dest='root_dir',
                        help='The root directory [ None ]')

  def add_commands(self, subparsers):
    p = subparsers.add_parser('ensure', help='Ensure a bes project is setup.')
    p.add_argument('--version', action='append', type=str, default=[],
                   dest='versions',
                   help='The version of python to use [ None ]')
    p.add_argument('--requirements-dev', action='store', type=str, default=None,
                   dest='requirements_dev',
                   help='The optional requirements-dev.txt file [ None ]')
    p.add_argument('requirements', action='store', type=str, default=None,
                   help='The requirements.txt file [ None ]')

    p = subparsers.add_parser('activate_script', help='Print the activate script for the virtual env.')
    p.add_argument('version', action='store', type=str, default=None,
                   help='The version of python [ None ]')
    p.add_argument('--variant', action='store', type=str, default=None,
                   help='The virtual env variant (csh, fish, ps1) [ None ]')

  def handler_class(self):
    from .bes_project_command_handler import bes_project_command_handler
    return bes_project_command_handler

  def supported_platforms(self):
    return 'all'
