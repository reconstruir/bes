#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check
from bes.common.string_util import string_util
from bes.key_value.key_value_list import key_value_list
from bes.text.text_table import text_table

from .vmware_client import vmware_client
from .vmware_client_options import vmware_client_options
from .vmware_error import vmware_error

class vmware_client_cli_command(cli_command_handler):
  'vmware client cli handler.'

  def __init__(self, cli_args):
    super(vmware_client_cli_command, self).__init__(cli_args, options_class = vmware_client_options)
    check.check_vmware_client_options(self.options)
    self._api = vmware_client(self.options.address, self.options.auth)

  def vms(self):
    vms = self._api.vms()
    tt = text_table(data = vms)
    tt.set_labels( ( 'NAME', 'ID', 'PATH' ) )
    print(tt)
    return 0

  def vm_settings(self, vm_id):
    check.check_string(vm_id)

    vm_id = self._resolve_vm_id(vm_id)
    settings = self._api.vm_settings(vm_id)
    print(pprint.pformat(settings))
    return 0
  
  def vm_config(self, vm_id, key):
    check.check_string(vm_id)
    check.check_string(key)
    
    vm_id = self._resolve_vm_id(vm_id)
    config = self._api.vm_config(vm_id, key)
    print(config)
    return 0

  def vm_power(self, vm_id, state, wait):
    check.check_string(vm_id)
    check.check_string(state, allow_none = True)
    check.check_string(wait, allow_none = True)

    vm_id = self._resolve_vm_id(vm_id)
    if state != None:
      self._api.vm_set_power(vm_id, state, wait = wait)
      if self.options.verbose:
        ip_address = self._api.vm_get_ip_address(vm_id)
        print(ip_address)
    else:
      power = self._api.vm_get_power(vm_id)
      print('on' if power else 'off')
    return 0

  def request(self, endpoint, args):
    check.check_string(endpoint)

    # Deal with situation where spacing around args is not consistent
    flat_args = string_util.replace(' '.join(args), { ' =': '=', ' = ': '=', '= ': '=' })
    params = key_value_list.parse(flat_args).to_dict()
    data = self._api.request(endpoint, params or None)
    print(pprint.pformat(data))
    return 0
  
  def vm_mac_address(self, vm_id):
    check.check_string(vm_id)
    
    vm_id = self._resolve_vm_id(vm_id)
    mac_address = self._api.vm_get_mac_address(vm_id)
    print(mac_address)
    return 0

  def vm_ip_address(self, vm_id):
    check.check_string(vm_id)
    
    vm_id = self._resolve_vm_id(vm_id)
    ip_address = self._api.vm_get_ip_address(vm_id)
    print(ip_address)
    return 0

  def vm_shared_folders(self, vm_id):
    check.check_string(vm_id)
    
    vm_id = self._resolve_vm_id(vm_id)
    shared_folders = self._api.vm_get_shared_folders(vm_id)
    tt = text_table(data = shared_folders)
    tt.set_labels( ( 'FOLDER_ID', 'PATH', 'PATH_ABS', 'FLAGS' ) )
    print(tt)
    return 0

  def vm_update_shared_folder(self, vm_id, folder_id, host_path, flags):
    check.check_string(vm_id)
    check.check_string(folder_id)
    check.check_string(host_path)
    check.check_int(flags)
    
    vm_id = self._resolve_vm_id(vm_id)
    shared_folders = self._api.vm_update_shared_folder(vm_id, folder_id, host_path, flags)
    tt = text_table(data = shared_folders)
    tt.set_labels( ( 'FOLDER_ID', 'PATH', 'PATH_ABS', 'FLAGS' ) )
    print(tt)
    return 0

  def vm_add_shared_folder(self, vm_id, folder_id, host_path, flags):
    check.check_string(vm_id)
    check.check_string(folder_id)
    check.check_string(host_path)
    check.check_int(flags)
    
    vm_id = self._resolve_vm_id(vm_id)
    shared_folders = self._api.vm_add_shared_folder(vm_id, folder_id, host_path, flags)
    tt = text_table(data = shared_folders)
    tt.set_labels( ( 'FOLDER_ID', 'PATH', 'PATH_ABS', 'FLAGS' ) )
    print(tt)
    return 0

  def vm_delete_shared_folder(self, vm_id, folder_id):
    check.check_string(vm_id)
    check.check_string(folder_id)
    
    vm_id = self._resolve_vm_id(vm_id)
    shared_folders = self._api.vm_delete_shared_folder(vm_id, folder_id)
    return 0

  def vm_delete_shared_folder(self, vm_id, folder_id):
    check.check_string(vm_id)
    check.check_string(folder_id)
    
    vm_id = self._resolve_vm_id(vm_id)
    shared_folders = self._api.vm_delete_shared_folder(vm_id, folder_id)
    return 0

  def vm_copy(self, vm_id, new_vm_id):
    check.check_string(vm_id)
    check.check_string(new_vm_id)
    
    vm_id = self._resolve_vm_id(vm_id)
    shared_folders = self._api.vm_copy(vm_id, new_vm_id)
    return 0

  def vm_delete(self, vm_id):
    check.check_string(vm_id)
    
    vm_id = self._resolve_vm_id(vm_id)
    shared_folders = self._api.vm_delete(vm_id)
    return 0
  
  def vm_restart(self, vm_id, wait):
    check.check_string(vm_id)
    check.check_string(wait, allow_none = True)
    
    vm_id = self._resolve_vm_id(vm_id)
    self._api.vm_set_power(vm_id, 'off')
    self._api.vm_set_power(vm_id, 'on', wait = wait)
    return 0
  
  def _resolve_vm_id(self, name):
    vm_id = self._api.vm_name_to_id(name)
    if not vm_id:
      raise vmware_error('Unknown vm: "{}"'.format(name))
    return vm_id
