#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class computer_setup_cli_args(object):

  def __init__(self):
    pass
  
  def computer_setup_add_args(self, subparser):

    # update
    p = subparser.add_parser('update', help = 'Update computer setup.')
    p.add_argument('config_filename', action = 'store', default = None,
                   help = 'The config to use [ None ]')
    p.add_argument('-v', '--verbose', action = 'store_true',
                   default = False, help = 'Verbose output')
    p.add_argument('--dry-run', action = 'store_true',
                   default = False, help = 'Do not do any work just print what would happen')
    
  def _command_computer_setup(self, command, *args, **kargs):
    from .computer_setup_cli_handler import computer_setup_cli_handler
    return computer_setup_cli_handler(kargs).handle_command(command)
