#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint

from ..system.check import check
from bes.key_value.key_value_list import key_value_list
from bes.text.text_table import text_table
from bes.text.text_replace import text_replace

from .bat_vmware_client import bat_vmware_client
from .bat_vmware_client_options import bat_vmware_client_options
from .vmware_error import vmware_error
from .bat_vmware_session_options import bat_vmware_session_options

class bat_vmware_client_commands(object):
  'vmware client commands.'

  def __init__(self, client, options):
    check.check_bat_vmware_client(client)
    check.check(options, ( bat_vmware_client_options, bat_vmware_session_options ))

    self._client = client
    self._options = options

  def vms(self):
    vms = self._client.vms()
    if not vms:
      return 0
    tt = text_table(data = vms)
    tt.set_labels( tuple([ f.upper() for f in vms[0]._fields ]) )
    print(tt)
    return 0

  def vm_settings(self, vm_id):
    check.check_string(vm_id)

    vm_id = self.resolve_vm_id(vm_id)
    settings = self._client.vm_settings(vm_id)
    print(pprint.pformat(settings))
    return 0
  
  def vm_config(self, vm_id, key):
    check.check_string(vm_id)
    check.check_string(key)
    
    vm_id = self.resolve_vm_id(vm_id)
    config = self._client.vm_config(vm_id, key)
    print(config)
    return 0

  def vm_power(self, vm_id, state, wait):
    check.check_string(vm_id)
    check.check_string(state, allow_none = True)
    check.check_string(wait, allow_none = True)

    vm_id = self.resolve_vm_id(vm_id)
    if state != None:
      self._client.vm_set_power(vm_id, state, wait = wait)
      if self._options.verbose:
        ip_address = self._client.vm_get_ip_address(vm_id)
        print(ip_address)
    else:
      power = self._client.vm_get_power(vm_id)
      print('on' if power else 'off')
    return 0

  def request(self, endpoint, args):
    check.check_string(endpoint)

    # Deal with situation where spacing around args is not consistent
    flat_args = text_replace.replace(' '.join(args), { ' =': '=', ' = ': '=', '= ': '=' }, word_boundary = False)
    params = key_value_list.parse(flat_args).to_dict()
    data = self._client.request(endpoint, params or None)
    print(pprint.pformat(data))
    return 0
  
  def vm_mac_address(self, vm_id):
    check.check_string(vm_id)
    
    vm_id = self.resolve_vm_id(vm_id)
    mac_address = self._client.vm_get_mac_address(vm_id)
    print(mac_address)
    return 0

  def vm_ip_address(self, vm_id):
    check.check_string(vm_id)
    
    vm_id = self.resolve_vm_id(vm_id)
    ip_address = self._client.vm_get_ip_address(vm_id)
    print(ip_address)
    return 0

  def vm_shared_folders(self, vm_id):
    check.check_string(vm_id)
    
    vm_id = self.resolve_vm_id(vm_id)
    shared_folders = self._client.vm_get_shared_folders(vm_id)
    tt = text_table(data = shared_folders)
    tt.set_labels( ( 'FOLDER_ID', 'PATH', 'PATH_ABS', 'FLAGS' ) )
    print(tt)
    return 0

  def vm_update_shared_folder(self, vm_id, folder_id, host_path, flags):
    check.check_string(vm_id)
    check.check_string(folder_id)
    check.check_string(host_path)
    check.check_int(flags)
    
    vm_id = self.resolve_vm_id(vm_id)
    shared_folders = self._client.vm_update_shared_folder(vm_id, folder_id, host_path, flags)
    tt = text_table(data = shared_folders)
    tt.set_labels( ( 'FOLDER_ID', 'PATH', 'PATH_ABS', 'FLAGS' ) )
    print(tt)
    return 0

  def vm_add_shared_folder(self, vm_id, folder_id, host_path, flags):
    check.check_string(vm_id)
    check.check_string(folder_id)
    check.check_string(host_path)
    check.check_int(flags)
    
    vm_id = self.resolve_vm_id(vm_id)
    shared_folders = self._client.vm_add_shared_folder(vm_id, folder_id, host_path, flags)
    tt = text_table(data = shared_folders)
    tt.set_labels( ( 'FOLDER_ID', 'PATH', 'PATH_ABS', 'FLAGS' ) )
    print(tt)
    return 0

  def vm_delete_shared_folder(self, vm_id, folder_id):
    check.check_string(vm_id)
    check.check_string(folder_id)
    
    vm_id = self.resolve_vm_id(vm_id)
    shared_folders = self._client.vm_delete_shared_folder(vm_id, folder_id)
    return 0

  def vm_delete_shared_folder(self, vm_id, folder_id):
    check.check_string(vm_id)
    check.check_string(folder_id)
    
    vm_id = self.resolve_vm_id(vm_id)
    shared_folders = self._client.vm_delete_shared_folder(vm_id, folder_id)
    return 0

  def vm_copy(self, vm_id, new_vm_id):
    check.check_string(vm_id)
    check.check_string(new_vm_id)
    
    vm_id = self.resolve_vm_id(vm_id)
    shared_folders = self._client.vm_copy(vm_id, new_vm_id)
    return 0

  def vm_delete(self, vm_id, force_shutdown):
    check.check_string(vm_id)
    check.check_bool(force_shutdown)
    
    vm_id = self.resolve_vm_id(vm_id)
    shared_folders = self._client.vm_delete(vm_id, force_shutdown)
    return 0
  
  def vm_restart(self, vm_id, wait):
    check.check_string(vm_id)
    check.check_string(wait, allow_none = True)
    
    vm_id = self.resolve_vm_id(vm_id)
    self._client.vm_set_power(vm_id, 'off')
    self._client.vm_set_power(vm_id, 'on', wait = wait)
    return 0
  
  def resolve_vm_id(self, name):
    vm_id = self._client.vm_name_to_id(name)
    if not vm_id:
      raise vmware_error('Unknown vm: "{}"'.format(name))
    return vm_id
