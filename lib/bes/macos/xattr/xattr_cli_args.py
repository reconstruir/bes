#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class xattr_cli_args(object):

  def __init__(self):
    pass
  
  def xattr_add_args(self, subparser):

    # keys
    p = subparser.add_parser('keys', help = 'Print keys for a file.')
    p.add_argument('filename', action = 'store', default = None,
                   help = 'The file [ None ]')

  def _command_xattr(self, command, *args, **kargs):
    from .xattr_cli_handler import xattr_cli_handler
    return xattr_cli_handler(kargs).handle_command(command)
