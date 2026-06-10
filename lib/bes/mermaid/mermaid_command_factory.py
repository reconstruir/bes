#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

class mermaid_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'mermaid'

  @classmethod
  def description(clazz):
    return 'Generate and render mermaid diagrams'

  def error_class(self):
    from .mermaid_error import mermaid_error
    raise mermaid_error

  def options_class(self):
    from .mermaid_command_options import mermaid_command_options
    return mermaid_command_options

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Verbose output [ False ]')
    parser.add_argument('-d', '--debug', action='store_true', default=False,
                        help='Debug mode [ False ]')

  def add_commands(self, subparsers):
    p = subparsers.add_parser('generate', help='Generate state machine classes.')
    p.add_argument('filename', action='store', default=None,
                   help='The mmd filename')
    p.add_argument('name', action='store', default=None,
                   help='The name of the lexer')
    p.add_argument('namespace', action='store', default=None,
                   help='The namespace of the lexer')
    p.add_argument('output_directory', action='store', default=None,
                   help='The output directory')

    p = subparsers.add_parser('make', help='Make a diagram image from an mmd file.')
    p.add_argument('-f', '--format', action='store', default='svg',
                   dest='output_format', choices=('svg', 'jpg'),
                   help='The output format [ svg ]')
    p.add_argument('filename', action='store', default=None,
                   help='The mmd filename')
    p.add_argument('output_filename', action='store', default=None,
                   help='The output image filename')

  def handler_class(self):
    from .mermaid_command_handler import mermaid_command_handler
    return mermaid_command_handler

  def supported_platforms(self):
    return 'all'
