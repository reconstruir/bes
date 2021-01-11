#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check
from bes.common.string_util import string_util
from bes.key_value.key_value_list import key_value_list
from bes.text.text_table import text_table

from .vmware_client import vmware_client
from .vmware_error import vmware_error
from .vmware_session_options import vmware_session_options
from .vmware_server import vmware_server
from .vmware_session import vmware_session

class vmware_session_cli_command(cli_command_handler):
  'vmware cli handler.'

  def __init__(self, cli_args):
    super(vmware_session_cli_command, self).__init__(cli_args, options_class = vmware_session_options)
    check.check_vmware_session_options(self.options)
    self._session = vmware_session(port = None, credentials = None)

  def vms(self):
    self._session.start()
    vms = self._session.call_client('vms')
    tt = text_table(data = vms)
    tt.set_labels( ( 'NAME', 'ID', 'PATH' ) )
    print(tt)
    self._session.stop()
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
