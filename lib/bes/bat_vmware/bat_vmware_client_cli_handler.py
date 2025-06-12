#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint

from bes.cli.cli_command_handler import cli_command_handler
from ..system.check import check

from .bat_vmware_client import bat_vmware_client
from .bat_vmware_client_commands import bat_vmware_client_commands
from .bat_vmware_client_options import bat_vmware_client_options

class bat_vmware_client_cli_handler(cli_command_handler):
  'vmware client cli handler.'

  def __init__(self, cli_args):
    super(bat_vmware_client_cli_handler, self).__init__(cli_args, options_class = bat_vmware_client_options)
    check.check_bat_vmware_client_options(self.options)
    client = bat_vmware_client(self.options.address, self.options.auth)
    self._commands = bat_vmware_client_commands(client, self.options)

  def vms(self):
    return self._commands.vms()

  def vm_settings(self, vm_id):
    return self._commands.vm_settings(vm_id)
  
  def vm_config(self, vm_id, key):
    return self._commands.vm_config(vm_id, key)

  def vm_power(self, vm_id, state, wait):
    return self._commands.vm_power(vm_id, state, wait)

  def request(self, endpoint, args):
    return self._commands.request(endpoint, args)
  
  def vm_mac_address(self, vm_id):
    return self._commands.vm_mac_address(vm_id)

  def vm_ip_address(self, vm_id):
    return self._commands.vm_ip_address(vm_id)

  def vm_shared_folders(self, vm_id):
    return self._commands.vm_shared_folders(vm_id)

  def vm_update_shared_folder(self, vm_id, folder_id, host_path, flags):
    return self._commands.vm_update_shared_folder(vm_id, folder_id, host_path, flags)

  def vm_add_shared_folder(self, vm_id, folder_id, host_path, flags):
    return self._commands.vm_add_shared_folder(vm_id, folder_id, host_path, flags)

  def vm_delete_shared_folder(self, vm_id, folder_id):
    return self._commands.vm_delete_shared_folder(vm_id, folder_id)

  def vm_copy(self, vm_id, new_vm_id):
    return self._commands.vm_copy(vm_id, new_vm_id)

  def vm_delete(self, vm_id):
    return self._commands.vm_delete(vm_id)
  
  def vm_restart(self, vm_id, wait):
    return self._commands.vm_restart(vm_id)
