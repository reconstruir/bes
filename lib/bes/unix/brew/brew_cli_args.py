#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class brew_cli_args(object):

  def __init__(self):
    pass
  
  def brew_add_args(self, subparser):

    # info
    p = subparser.add_parser('info', help = 'Print the brew version.')
    
  def __brew_add_common_args(self, p):
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')

  def _command_brew(self, command, *args, **kargs):
    from .brew_cli_handler import brew_cli_handler
    return brew_cli_handler(kargs).handle_command(command)
  
