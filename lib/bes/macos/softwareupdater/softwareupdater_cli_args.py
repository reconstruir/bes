#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class softwareupdater_cli_args(object):

  def __init__(self):
    pass
  
  def softwareupdater_add_args(self, subparser):

    # available
    p = subparser.add_parser('available', help = 'Print available updates.')
    p.add_argument('--force-command-line-tools', action = 'store_true', default = False,
                   help = 'Force the xcode command line tools to appear in list [ False ]')

    # install
    p = subparser.add_parser('install', help = 'Install an item by label.')
    p.add_argument('label', action = 'store', default = None,
                   help = 'Label of the item to install [ None ]')
    
  def _command_softwareupdater(self, command, *args, **kargs):
    from .softwareupdater_cli_command import softwareupdater_cli_command
    return softwareupdater_cli_command.handle_command(command, **kargs)
