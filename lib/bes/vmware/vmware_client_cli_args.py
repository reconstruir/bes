#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class vmware_client_cli_args(object):

  def __init__(self):
    pass
  
  def vmware_client_add_args(self, subparser):

    # vms
    p = subparser.add_parser('vms', help = 'Return a list of vms.')
    self.__vmware_client_add_common_args(p)
    
  def __vmware_client_add_common_args(self, p):
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('-p', '--port', action = 'store', type = int, default = None,
                   help = 'Port [ 8697 ]')
    p.add_argument('--hostname', action = 'store', type = str, default = 'localhost',
                   help = 'Hostname [ localhost ]')
    p.add_argument('-u', '--username', action = 'store', type = str, default = None,
                   help = 'Username [ ]')
    p.add_argument('-p', '--password', action = 'store', type = str, default = None,
                   help = 'Password [ ]')
    
  def _command_vmware_client(self, command, *args, **kargs):
    from .vmware_client_cli_command import vmware_client_cli_command
    return vmware_client_cli_command(kargs).handle_command(command)
