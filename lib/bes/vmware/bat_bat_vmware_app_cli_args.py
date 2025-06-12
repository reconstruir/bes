#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class bat_bat_vmware_app_cli_args(object):

  def __init__(self):
    pass
  
  def bat_vmware_app_add_args(self, subparser):

    # is_installed
    p = subparser.add_parser('is_installed', help = 'Check if vmware is installed.')
    self.__bat_vmware_app_add_common_args(p)
    
    # is_running
    p = subparser.add_parser('is_running', help = 'Check if vmware is running.')
    self.__bat_vmware_app_add_common_args(p)

    # ensure_running
    p = subparser.add_parser('ensure_running', help = 'Ensure vmware is running.')
    self.__bat_vmware_app_add_common_args(p)

    # ensure_stopped
    p = subparser.add_parser('ensure_stopped', help = 'Ensure vmware is stopped.')
    self.__bat_vmware_app_add_common_args(p)

    # install_path
    p = subparser.add_parser('install_path', help = 'Print the app installation path.')
    self.__bat_vmware_app_add_common_args(p)

    # vmrun
    p = subparser.add_parser('vmrun', help = 'Print the vmrun exe path.')
    self.__bat_vmware_app_add_common_args(p)

    # vmrest
    p = subparser.add_parser('vmrest', help = 'Print the vmrest exe path.')
    self.__bat_vmware_app_add_common_args(p)
    
    # ovftool
    p = subparser.add_parser('ovftool', help = 'Print the ovftool exe path.')
    self.__bat_vmware_app_add_common_args(p)

  def __bat_vmware_app_add_common_args(self, p):
    'Add argument common to all commands that run programs and scripts'
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    
  def _command_bat_vmware_app(self, command, *args, **kargs):
    from .bat_bat_vmware_app_cli_handler import bat_bat_vmware_app_cli_handler
    return bat_bat_vmware_app_cli_handler(kargs).handle_command(command)
