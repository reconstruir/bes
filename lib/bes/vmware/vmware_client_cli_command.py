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

  def vms(self):
    api = vmware_client_api(self.options.address, self.options.auth)
    vms = api.vms()
    for vm in vms:
      print(vm)
    return 0
