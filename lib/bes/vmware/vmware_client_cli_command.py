#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check

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
  
