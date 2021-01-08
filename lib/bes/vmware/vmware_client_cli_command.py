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
  
