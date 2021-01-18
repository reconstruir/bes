#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class vmware_app_cli_args(object):

  def __init__(self):
    pass
  
  def vmware_app_add_args(self, subparser):

    # is_installed
    p = subparser.add_parser('is_installed', help = 'Check if vmware is installed.')
    
    # is_running
    p = subparser.add_parser('is_running', help = 'Check if vmware is running.')

    # ensure_running
    p = subparser.add_parser('ensure_running', help = 'Ensure vmware is running.')
    
  def _command_vmware_app(self, command, *args, **kargs):
    from .vmware_app_cli_handler import vmware_app_cli_handler
    return vmware_app_cli_handler(kargs).handle_command(command)
