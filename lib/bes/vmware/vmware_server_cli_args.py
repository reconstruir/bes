#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class vmware_server_cli_args(object):

  def __init__(self):
    pass
  
  def vmware_server_add_args(self, subparser):

    # shell
    p = subparser.add_parser('shell', help = 'Run interactive vmrest shell.')
    self.__vmware_server_add_common_args(p)
    p.add_argument('shell_args', action = 'store', default = [], nargs = '*',
                   help = 'Shell args. [ None ]')

    # set_credentials
    p = subparser.add_parser('set_credentials', help = 'Set the server username and password.')
    p.add_argument('username', action = 'store', default = None,
                   help = 'The username. [ None ]')
    p.add_argument('password', action = 'store', default = None,
                   help = 'The password. [ None ]')
    p.add_argument('-n', '--num-tries', action = 'store', default = None,
                   help = 'Number of set credentials tries.  It can be flaky. [ 1 ]')
    
  def __vmware_server_add_common_args(self, p):
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('-p', '--port', action = 'store', type = int, default = None,
                   help = 'Port [ 8697 ]')
    
  def _command_vmware_server(self, command, *args, **kargs):
    from .bat_vmware_server_cli_handler import bat_vmware_server_cli_handler
    return bat_vmware_server_cli_handler(kargs).handle_command(command)
