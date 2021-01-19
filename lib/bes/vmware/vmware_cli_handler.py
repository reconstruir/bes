#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check

from .vmware import vmware

class vmware_cli_handler(cli_command_handler):
  'vmware preferences cli handler.'

  def __init__(self, cli_args):
    super(vmware_cli_handler, self).__init__(cli_args)
    self._vmware = vmware()

  def vm_run_program(self, vm_id, username, password, program, copy_vm):
    rv = self._vmware.run_program(vm_id, username, password, program, copy_vm)
    return rv.exit_code
