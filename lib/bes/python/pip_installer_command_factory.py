#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

class pip_installer_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'pip_installer'

  @classmethod
  def description(clazz):
    return 'Install and manage pip'

  def error_class(self):
    from .pip_error import pip_error
    raise pip_error

  def options_class(self):
    from .pip_installer_command_options import pip_installer_command_options
    return pip_installer_command_options

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Verbose output [ False ]')
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Debug mode [ False ]')
    parser.add_argument('-r', '--root-dir', action='store', default=None,
                        dest='root_dir',
                        help='The root directory where to install pip [ None ]')
    parser.add_argument('-p', '--python', action='store', default=None,
                        dest='python_exe',
                        help='The python executable to use [ None ]')

  def add_commands(self, subparsers):
    p = subparsers.add_parser('install', help='Install pip to a new root dir.')
    p.add_argument('pip_version', action='store', type=str, default=None,
                   help='The pip version [ None ]')
    p.add_argument('name', action='store', type=str, default=None,
                   help='The name for this pip installation [ None ]')
    p.add_argument('--clobber', action='store_true', default=False,
                   dest='clobber_install_dir',
                   help='Clobber the install dir if it exists [ False ]')

    p = subparsers.add_parser('update', help='Update pip to a specific version or install it if needed.')
    p.add_argument('pip_version', action='store', type=str, default=None,
                   help='The pip version [ None ]')
    p.add_argument('name', action='store', type=str, default=None,
                   help='The name for this pip installation [ None ]')

    p = subparsers.add_parser('uninstall', help='Uninstall pip.')
    p.add_argument('name', action='store', type=str, default=None,
                   help='The name for this pip installation [ None ]')

  def handler_class(self):
    from .pip_installer_command_handler import pip_installer_command_handler
    return pip_installer_command_handler

  def supported_platforms(self):
    return 'all'
