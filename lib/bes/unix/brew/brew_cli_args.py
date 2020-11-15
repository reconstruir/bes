#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class brew_cli_args(object):

  def __init__(self):
    pass
  
  def brew_add_args(self, subparser):

    # run_script
    p = subparser.add_parser('run_script', help = 'Download and run a brew script.')
    p.add_argument('script_name', action = 'store', default = None,
                   help = 'The name of the script such as install.sh or uninstall.sh [ None ]')
    p.add_argument('--print', action = 'store_true', default = False,
                   dest = 'print_only',
                   help = 'Print the script instead of running it [ False ]')
    p.add_argument('args', action = 'store', default = None, nargs = '*',
                   help = 'Arguments for the script [ ]')

  def _command_brew(self, command, *args, **kargs):
    from .brew_cli_command import brew_cli_command
    return brew_cli_command.handle_command(command, **kargs)
