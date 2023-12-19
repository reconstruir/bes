#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class btl_cli_args(object):

  def __init__(self):
    pass
  
  def btl_add_args(self, subparser):

    # make_mmd
    p = subparser.add_parser('make_mmd', help = 'Generate the mermaid mmd state diagram.')
    self.__btl_cli_add_add_common_args(p)
    p.add_argument('filename', action = 'store', default = None,
                   help = 'The btl filename')
    p.add_argument('output_filename', action = 'store', default = None,
                   help = 'The output mmd filename')

    # make_diagram
    p = subparser.add_parser('make_diagram', help = 'Make a diagram jpeg/svg from an mmd file.')
    self.__btl_cli_add_add_common_args(p)
    p.add_argument('-f', '--format', action = 'store', default = 'svg',
                   dest = 'output_format', choices = ( 'svg', 'jpg' ),
                   help = 'The output format.  svg or jpg [ svg ]')
    p.add_argument('filename', action = 'store', default = None,
                   help = 'The btl filename')
    p.add_argument('output_filename', action = 'store', default = None,
                   help = 'The output jpeg filename')
    
  @classmethod
  def __btl_cli_add_add_common_args(clazz, p):
    p.add_argument('--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('-d', '--debug', action = 'store_true', default = False,
                   help = 'Debug mode [ False ]')
    
  def _command_btl(self, command, *args, **kargs):
    from .btl_cli_handler import btl_cli_handler
    return btl_cli_handler(kargs).handle_command(command)
