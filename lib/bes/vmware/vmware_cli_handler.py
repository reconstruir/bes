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

  def vm_run_program(self, vm_id, username, password, program, copy_vm, dont_ensure):
    rv = self._vmware.vm_run_program(vm_id, username, password, program, copy_vm, dont_ensure)
    return rv.exit_code

  def vm_run_package(self, vm_id, username, password, package_dir,
                     entry_command, entry_command_args, copy_vm,
                     dont_ensure, output_filename, tail_log,
                     debug, tty):
    rv = self._vmware.vm_run_package(vm_id, username, password, package_dir,
                                     entry_command, entry_command_args, copy_vm,
                                     dont_ensure, output_filename, tail_log,
                                     debug, tty)
    return rv.exit_code

  def vm_clone(self, vm_id, dst_vmx_filename, full, snapshot_name, clone_name):
    rv = self._vmware.clone(vm_id,
                            dst_vmx_filename,
                            full = full,
                            snapshot_name = snapshot_name,
                            clone_name = clone_name)
    return rv.exit_code

  def vm_copy_to(self, vm_id, username, password, local_filename, remote_filename, dont_ensure):
    self._vmware.vm_copy_to(vm_id, username, password, local_filename, remote_filename, dont_ensure)
    return 0

  def vm_copy_from(self, vm_id, username, password, remote_filename, local_filename, dont_ensure):
    self._vmware.vm_copy_from(vm_id, username, password, remote_filename, local_filename, dont_ensure)
    return 0

  def vm_set_power(self, vm_id, state, wait, username, password, num_tries):
    self._vmware.vm_set_power(vm_id, state, wait, username, password, num_tries)
    return 0
