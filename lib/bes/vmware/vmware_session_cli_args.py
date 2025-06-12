#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class vmware_session_cli_args(object):

  def __init__(self):
    pass
  
  def vmware_session_add_args(self, subparser):

    # vms
    p = subparser.add_parser('vms', help = 'Return a list of vms.')
    self.__vmware_session_add_common_args(p)

    # vm_settings
    p = subparser.add_parser('vm_settings', help = 'Return settings for a vm.')
    self.__vmware_session_add_common_args(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')

    # vm_config
    p = subparser.add_parser('vm_config', help = 'Return config for a vm.')
    self.__vmware_session_add_common_args(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('key', action = 'store', type = str, default = None,
                   help = 'Config param key [ ]')

    # vm_power
    p = subparser.add_parser('vm_power', help = 'Get or set the vm power.')
    self.__vmware_session_add_common_args(p)
    p.add_argument('--wait', action = 'store', default = None,
                   choices = ( 'ip', 'ssh', 'none' ),
                   help = 'Wait until the ip address is known or ssh server is up [ none ]')
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('state', action = 'store', type = str, default = None, nargs = '?',
                   choices = ( 'on', 'off', 'shutdown', 'suspend', 'pause', 'unpause' ),
                   help = 'The new power state [ ]')

    # request
    p = subparser.add_parser('request', help = 'Make a generic request.')
    self.__vmware_session_add_common_args(p)
    p.add_argument('endpoint', action = 'store', default = None, type = str,
                   help = 'The request end point. [ None ]')
    p.add_argument('args', action = 'store', default = [], nargs = '*',
                   help = 'The script args. [ None ]')

    # vm_mac_address
    p = subparser.add_parser('vm_mac_address', help = 'Return mac_address for a vm.')
    self.__vmware_session_add_common_args(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')

    # vm_ip_address
    p = subparser.add_parser('vm_ip_address', help = 'Return ip_address for a vm.')
    self.__vmware_session_add_common_args(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')

    # vm_delete
    p = subparser.add_parser('vm_delete', help = 'Delete a vm.')
    self.__vmware_session_add_common_args(p)
    p.add_argument('--shutdown', action = 'store_true', default = False,
                   dest = 'force_shutdown',
                   help = 'Force the vm to shutdown first [ False ]')
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    
  def __vmware_session_add_common_args(self, p):
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('--vmrest-username', action = 'store', type = str, default = None,
                   help = 'Username for vmrest.  None means generate a random one. [ None ]')
    p.add_argument('--vmrest-password', action = 'store', type = str, default = None,
                   help = 'Password for vmrest.  None means generate a random one. [ None ]')
    p.add_argument('--vmrest-port', action = 'store', type = int, default = 8697,
                   dest = 'vmrest_port',
                   help = 'Port for vmrest [ 8697 ]')
    p.add_argument('--config', action = 'store', type = str, default = None,
                   dest = 'config_filename',
                   help = 'Use config filename [ False ]')
    
  def _command_vmware_session(self, command, *args, **kargs):
    from .bat_vmware_session_cli_handler import bat_vmware_session_cli_handler
    return bat_vmware_session_cli_handler(kargs).handle_command(command)
