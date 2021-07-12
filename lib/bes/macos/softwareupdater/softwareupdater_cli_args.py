#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class softwareupdater_cli_args(object):

  def __init__(self):
    pass
  
  def softwareupdater_add_args(self, subparser):

    # available
    p = subparser.add_parser('available', help = 'Print available updates.')
    p.add_argument('-f', '--force-command-line-tools', action = 'store_true', default = False,
                   help = 'Force the command line tools to be available [ False ]')

    # install
    p = subparser.add_parser('install', help = 'Install an item by label.')
    p.add_argument('label', action = 'store', default = None,
                   help = 'Label of the item to install [ None ]')
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    
  def _command_softwareupdater(self, command, *args, **kargs):
    from .softwareupdater_cli_handler import softwareupdater_cli_handler
    return softwareupdater_cli_handler.handle_command(command, **kargs)
