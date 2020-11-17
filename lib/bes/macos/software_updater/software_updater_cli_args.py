#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class software_updater_cli_args(object):

  def __init__(self):
    pass
  
  def software_updater_add_args(self, subparser):

    # available
    p = subparser.add_parser('available', help = 'Print available updates.')
    
  def _command_software_updater(self, command, *args, **kargs):
    from .software_updater_cli_command import software_updater_cli_command
    return software_updater_cli_command.handle_command(command, **kargs)
