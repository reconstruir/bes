#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class bat_vmware_client_cli_args(object):

  def __init__(self):
    pass
  
  def bat_vmware_client_add_args(self, subparser):

    # vms
    p = subparser.add_parser('vms', help = 'Return a list of vms.')
    self.__bat_vmware_client_add_common_args(p)

    # vm_settings
    p = subparser.add_parser('vm_settings', help = 'Return settings for a vm.')
    self.__bat_vmware_client_add_common_args(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')

    # vm_config
    p = subparser.add_parser('vm_config', help = 'Return config for a vm.')
    self.__bat_vmware_client_add_common_args(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('key', action = 'store', type = str, default = None,
                   help = 'Config param key [ ]')

    # vm_power
    p = subparser.add_parser('vm_power', help = 'Get or set the vm power.')
    self.__bat_vmware_client_add_common_args(p)
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
    self.__bat_vmware_client_add_common_args(p)
    p.add_argument('endpoint', action = 'store', default = None, type = str,
                   help = 'The request end point. [ None ]')
    p.add_argument('args', action = 'store', default = [], nargs = '*',
                   help = 'The script args. [ None ]')

    # vm_mac_address
    p = subparser.add_parser('vm_mac_address', help = 'Return mac_address for a vm.')
    self.__bat_vmware_client_add_common_args(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')

    # vm_ip_address
    p = subparser.add_parser('vm_ip_address', help = 'Return ip_address for a vm.')
    self.__bat_vmware_client_add_common_args(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')

    # vm_shared_folders
    p = subparser.add_parser('vm_shared_folders', help = 'Return shared folders for a vm.')
    self.__bat_vmware_client_add_common_args(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')

    # vm_update_shared_folder
    p = subparser.add_parser('vm_update_shared_folder', help = 'add a shared folder.')
    self.__bat_vmware_client_add_common_args(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'the vm id [ ]')
    p.add_argument('folder_id', action = 'store', type = str, default = None,
                   help = 'the folder_id [ ]')
    p.add_argument('host_path', action = 'store', type = str, default = None,
                   help = 'the host_path [ ]')
    p.add_argument('flags', action = 'store', type = int, default = None,
                   help = 'the flags [ ]')

    # vm_add_shared_folder
    p = subparser.add_parser('vm_add_shared_folder', help = 'Add a shared folder.')
    self.__bat_vmware_client_add_common_args(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('folder_id', action = 'store', type = str, default = None,
                   help = 'The folder_id [ ]')
    p.add_argument('host_path', action = 'store', type = str, default = None,
                   help = 'The host_path [ ]')
    p.add_argument('flags', action = 'store', type = int, default = None,
                   help = 'The flags [ ]')

    # vm_delete_shared_folder
    p = subparser.add_parser('vm_delete_shared_folder', help = 'delete a shared folder.')
    self.__bat_vmware_client_add_common_args(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('folder_id', action = 'store', type = str, default = None,
                   help = 'The folder_id [ ]')

    # vm_copy
    p = subparser.add_parser('vm_copy', help = 'Copy a vm.')
    self.__bat_vmware_client_add_common_args(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('new_vm_id', action = 'store', type = str, default = None,
                   help = 'The new vm id [ ]')

    # vm_delete
    p = subparser.add_parser('vm_delete', help = 'Delete a vm.')
    self.__bat_vmware_client_add_common_args(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    
    # vm_restart
    p = subparser.add_parser('vm_restart', help = 'Restart a vm.')
    self.__bat_vmware_client_add_common_args(p)
    p.add_argument('--wait', action = 'store', default = None,
                   choices = ( 'ip', 'ssh', 'none' ),
                   help = 'Wait until the ip address is known or ssh server is up [ none ]')
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    
  def __bat_vmware_client_add_common_args(self, p):
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('-p', '--port', action = 'store', type = int, default = 8697,
                   help = 'Port [ 8697 ]')
    p.add_argument('--hostname', action = 'store', type = str, default = 'localhost',
                   help = 'Hostname [ localhost ]')
    p.add_argument('--username', action = 'store', type = str, default = None,
                   help = 'Username [ ]')
    p.add_argument('--password', action = 'store', type = str, default = None,
                   help = 'Password [ ]')
    
  def _command_bat_vmware_client(self, command, *args, **kargs):
    from .bat_bat_vmware_client_cli_handler import bat_bat_vmware_client_cli_handler
    return bat_bat_vmware_client_cli_handler(kargs).handle_command(command)
