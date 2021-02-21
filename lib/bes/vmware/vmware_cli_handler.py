#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check
from bes.system.log import logger

from .vmware import vmware
from .vmware_options import vmware_options

class vmware_cli_handler(cli_command_handler):
  'vmware preferences cli handler.'

  _log = logger('vmware_cli_handler')
  
  def __init__(self, cli_args):
    super(vmware_cli_handler, self).__init__(cli_args, options_class = vmware_options)
    check.check_vmware_options(self.options)
    self._vmware = vmware(self.options)
    
  def vm_run_program(self, vm_id, program, interactive):
    rv = self._vmware.vm_run_program(vm_id, program, interactive)
    return rv.exit_code

  def vm_run_package(self, vm_id, package_dir, entry_command, entry_command_args,
                     interactive, output_filename, tail_log):
    rv = self._vmware.vm_run_package(vm_id,
                                     package_dir,
                                     entry_command,
                                     entry_command_args,
                                     interactive,
                                     output_filename,
                                     tail_log)
    return rv.exit_code

  def vm_clone(self, vm_id, dst_vmx_filename, full, snapshot_name, clone_name):
    self._vmware.vm_clone(vm_id,
                          dst_vmx_filename,
                          full = full,
                          snapshot_name = snapshot_name,
                          clone_name = clone_name)
    return 0

  def vm_copy_to(self, vm_id, local_filename, remote_filename):
    self._vmware.vm_copy_to(vm_id, local_filename, remote_filename)
    return 0

  def vm_copy_from(self, vm_id, remote_filename, local_filename):
    self._vmware.vm_copy_from(vm_id, remote_filename, local_filename)
    return 0

  def vm_set_power_state(self, vm_id, state, wait):
    self._vmware.vm_set_power_state(vm_id, state, wait)
    return 0

  def vm_command(self, vm_id, command, command_args):
    rv = self._vmware.vm_command(vm_id, command, command_args)
    print(rv.stdout)
    return rv.exit_code
