#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class mermaid_cli_args(object):

  def __init__(self):
    pass
  
  def mermaid_add_args(self, subparser):

    # generate
    p = subparser.add_parser('generate', help = 'Generate state machine classes.')
    self.__mermaid_cli_add_add_common_args(p)
    p.add_argument('filename', action = 'store', default = None,
                   help = 'The mmd filename')
    p.add_argument('name', action = 'store', default = None,
                   help = 'The name of the lexer')
    p.add_argument('namespace', action = 'store', default = None,
                   help = 'The namespace of the lexer')
    p.add_argument('output_directory', action = 'store', default = None,
                   help = 'The output filename')

    # make
    p = subparser.add_parser('make', help = 'Make a diagram jpeg from an mmd file.')
    self.__mermaid_cli_add_add_common_args(p)
    p.add_argument('-f', '--format', action = 'store', default = 'svg',
                   dest = 'output_format', choices = ( 'svg', 'jpg' ),
                   help = 'The output format.  svg or jpg [ svg ]')
    p.add_argument('filename', action = 'store', default = None,
                   help = 'The mmd filename')
    p.add_argument('output_filename', action = 'store', default = None,
                   help = 'The output jpeg filename')
    
  @classmethod
  def __mermaid_cli_add_add_common_args(clazz, p):
    p.add_argument('--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('-d', '--debug', action = 'store_true', default = False,
                   help = 'Debug mode [ False ]')
    
  def _command_mermaid(self, command, *args, **kargs):
    from .mermaid_cli_handler import mermaid_cli_handler
    return mermaid_cli_handler(kargs).handle_command(command)
