#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class sudo_cli_args(object):

  def __init__(self):
    pass
  
  def sudo_add_args(self, subparser):

    # command
    p = subparser.add_parser('run', help = 'Run a command with sudo.')
    self.__sudo_cli_args_add_common_args(p)
    p.add_argument('cmd', action = 'store', default = None, nargs = '+',
                   help = 'Command to run [ ]')

    # authenticate
    p = subparser.add_parser('authenticate', help = 'Authenticate with sudo.')
    self.__sudo_cli_args_add_common_args(p)
    p.add_argument('--force', action = 'store_true', default = False,
                   dest = 'force_auth',
                   help = 'Force auth even if already authenticated [ False ]')

    # is_authenticated
    p = subparser.add_parser('is_authenticated', help = 'Return 0 if authenticated 1 otherwise.')
    self.__sudo_cli_args_add_common_args(p)
    
    # reset
    p = subparser.add_parser('reset', help = 'Reset authentication.')
    self.__sudo_cli_args_add_common_args(p)
    
  def __sudo_cli_args_add_common_args(self, p):
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('--password', action = 'store', default = None,
                   help = 'The sudo password to use [ ]')
    p.add_argument('--prompt', action = 'store', default = None,
                   help = 'The sudo prompt to use [ ]')
    p.add_argument('--working-dir', action = 'store', default = None,
                   help = 'The sudo password to use [ ]')
    
  def _command_sudo(self, command, *args, **kargs):
    from .sudo_cli_handler import sudo_cli_handler
    return sudo_cli_handler.handle_command(command, **kargs)
