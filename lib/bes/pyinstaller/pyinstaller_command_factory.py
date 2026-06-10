#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

from .pyinstaller_defaults import pyinstaller_defaults

class pyinstaller_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'pyinstaller'

  @classmethod
  def description(clazz):
    return 'Build executables with PyInstaller'

  def error_class(self):
    from .pyinstaller_error import pyinstaller_error
    raise pyinstaller_error

  def options_class(self):
    from .pyinstaller_command_options import pyinstaller_command_options
    return pyinstaller_command_options

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Verbose output [ False ]')
    parser.add_argument('-d', '--debug', action='store_true', default=False,
                        help='Debug mode [ False ]')

  def add_commands(self, subparsers):
    p = subparsers.add_parser('build', help='Build a pyinstaller executable.')
    p.add_argument('--build-dir', action='store', default=pyinstaller_defaults.BUILD_DIR,
                   dest='build_dir',
                   help=f'Build dir [ {pyinstaller_defaults.BUILD_DIR} ]')
    p.add_argument('--clean', action='store_true', default=False,
                   help='Clean first [ False ]')
    p.add_argument('--windowed', action='store_true', default=pyinstaller_defaults.WINDOWED,
                   help=f'Windowed [ {pyinstaller_defaults.WINDOWED} ]')
    p.add_argument('--osx-bundle-identifier', action='store', default=None,
                   dest='osx_bundle_identifier',
                   help='Mac OS X .app bundle identifier [ None ]')
    p.add_argument('--exclude', action='append', default=[],
                   dest='excludes',
                   help='Exclude the given python module [ ]')
    p.add_argument('--hidden-import', action='append', default=[],
                   dest='hidden_imports',
                   help='Force include the given hidden import [ ]')
    p.add_argument('--log-level', action='store', default=pyinstaller_defaults.LOG_LEVEL,
                   dest='log_level',
                   choices=pyinstaller_defaults.LOG_LEVEL_CHOICES,
                   help=f'PyInstaller log level [ {pyinstaller_defaults.LOG_LEVEL.name} ]')
    p.add_argument('--python-version', action='store', default='3.8',
                   dest='python_version',
                   help='The python version to use [ 3.8 ]')
    p.add_argument('script_filename', action='store', default=None,
                   help='The python script [ ]')
    p.add_argument('output_filename', action='store', default=None,
                   help='The output exe filename [ ]')

  def handler_class(self):
    from .pyinstaller_command_handler import pyinstaller_command_handler
    return pyinstaller_command_handler

  def supported_platforms(self):
    return 'all'
