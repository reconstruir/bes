#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class vmware_cli_args(object):

  def __init__(self):
    pass
  
  def vmware_add_args(self, subparser):

    # is_running
    p = subparser.add_parser('is_running', help = 'Check if vmware is running.')

    # ensure_running
    p = subparser.add_parser('ensure_running', help = 'Ensure vmware is running.')
    
    # vm_run
    p = subparser.add_parser('vm_run', help = 'Ensure vmware is running.')
    
  def _command_vmware(self, command, *args, **kargs):
    from .vmware_cli_handler import vmware_cli_handler
    return vmware_cli_handler(kargs).handle_command(command)
