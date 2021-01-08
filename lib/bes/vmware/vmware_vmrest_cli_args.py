#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class vmware_vmrest_cli_args(object):

  def __init__(self):
    pass
  
  def vmware_vmrest_add_args(self, subparser):

    # shell
    p = subparser.add_parser('shell', help = 'Run interactive vmrest shell.')
    self.__vmware_vmrest_add_common_args(p)
    
  def __vmware_vmrest_add_common_args(self, p):
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('-p', '--port', action = 'store', type = int, default = None,
                   help = 'Port [ 8697 ]')
    
  def _command_vmware_vmrest(self, command, *args, **kargs):
    from .vmware_vmrest_cli_command import vmware_vmrest_cli_command
    return vmware_vmrest_cli_command(kargs).handle_command(command)
