#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class command_line_tools_cli_args(object):

  def __init__(self):
    pass
  
  def command_line_tools_add_args(self, subparser):

    # installed
    p = subparser.add_parser('installed', help = 'Return 0 if command line tools are installed.')

    # install
    p = subparser.add_parser('install', help = 'Install the command line tools.')
    
    # ensure
    p = subparser.add_parser('ensure', help = 'Ensure the command line tools.')
    
  def _command_command_line_tools(self, command, *args, **kargs):
    from .command_line_tools_cli_command import command_line_tools_cli_command
    return command_line_tools_cli_command.handle_command(command, **kargs)
