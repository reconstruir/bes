#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class scutil_cli_args(object):

  def __init__(self):
    pass
  
  def scutil_add_args(self, subparser):

    # get_value
    p = subparser.add_parser('get_value', help = 'Read a value.')
    p.add_argument('key', action = 'store', default = None,
                   help = 'The key [ None ]')

    # set_value
    p = subparser.add_parser('set_value', help = 'Set a a value.')
    p.add_argument('key', action = 'store', default = None,
                   help = 'The key [ None ]')
    p.add_argument('value', action = 'store', default = None,
                   help = 'The value [ None ]')
    
  def _command_scutil(self, command, *args, **kargs):
    from .scutil_cli_command import scutil_cli_command
    return scutil_cli_command.handle_command(command, **kargs)
