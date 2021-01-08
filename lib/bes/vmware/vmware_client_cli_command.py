#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check
from bes.key_value.key_value_list import key_value_list
from bes.common.string_util import string_util

from .vmware_client_api import vmware_client_api
from .vmware_client_options import vmware_client_options

class vmware_client_cli_command(cli_command_handler):
  'vmware client cli handler.'

  def __init__(self, cli_args):
    super(vmware_client_cli_command, self).__init__(cli_args, options_class = vmware_client_options)
    check.check_vmware_client_options(self.options)
    self._api = vmware_client_api(self.options.address, self.options.auth)

  def vms(self):
    vms = self._api.vms()
    for vm in vms:
      print(vm)
    return 0

  def vm_settings(self, vm_id):
    check.check_string(vm_id)
    
    settings = self._api.vm_settings(vm_id)
    print(settings)
    return 0
  
  def vm_config(self, vm_id, key):
    check.check_string(vm_id)
    check.check_string(key)
    
    config = self._api.vm_config(vm_id, key)
    print(config)
    return 0

  def vm_power(self, vm_id, state):
    check.check_string(vm_id)
    check.check_string(state, allow_none = True)

    if state != None:
      self._api.vm_set_power(vm_id, state)
    else:
      power = self._api.vm_get_power(vm_id)
      print(power)
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
    
    mac_address = self._api.vm_get_mac_address(vm_id)
    print(mac_address)
    return 0

  def vm_ip_address(self, vm_id):
    check.check_string(vm_id)
    
    ip_address = self._api.vm_get_ip_address(vm_id)
    print(ip_address)
    return 0
  
