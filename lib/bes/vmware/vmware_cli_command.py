#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check
from bes.common.string_util import string_util
from bes.key_value.key_value_list import key_value_list
from bes.text.text_table import text_table

from .vmware_client_api import vmware_client_api
from .vmware_error import vmware_error
from .vmware_options import vmware_options
from .vmware_server import vmware_server

class vmware_cli_command(cli_command_handler):
  'vmware cli handler.'

  def __init__(self, cli_args):
    super(vmware_cli_command, self).__init__(cli_args, options_class = vmware_options)
    check.check_vmware_options(self.options)
    #self._api = vmware_client_api(self.options.address, self.options.auth)

  def vms(self):
    #vms = self._api.vms()
    #tt = text_table(data = vms)
    #tt.set_labels( ( 'NAME', 'ID', 'PATH' ) )
    #print(tt)
    print('foo')
    return 0

  def vm_settings(self, vm_id):
    check.check_string(vm_id)

    return 0
  
  def vm_config(self, vm_id, key):
    check.check_string(vm_id)
    check.check_string(key)
    
    return 0

  def vm_power(self, vm_id, state, wait_for_ip_address):
    check.check_string(vm_id)
    check.check_string(state, allow_none = True)
    check.check_bool(wait_for_ip_address)

    return 0

  def request(self, endpoint, args):
    check.check_string(endpoint)

    return 0
  
  def vm_mac_address(self, vm_id):
    check.check_string(vm_id)
    
    return 0

  def vm_ip_address(self, vm_id):
    check.check_string(vm_id)
    
    return 0
