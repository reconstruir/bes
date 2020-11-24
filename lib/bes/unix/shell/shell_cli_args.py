#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class shell_cli_args(object):

  def __init__(self):
    pass
  
  def shell_add_args(self, subparser):

    # change
    p = subparser.add_parser('change', help = 'Change shells.')
    p.add_argument('new_shell', action = 'store', default = False,
                   help = 'The new shell [ False ]')
    p.add_argument('-p', '--password', action = 'store', default = None,
                   help = 'The sudo password [ None ]')
    
  def _command_shell(self, command, *args, **kargs):
    from .shell_cli_command import shell_cli_command
    return shell_cli_command.handle_command(command, **kargs)
