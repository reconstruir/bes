#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_command_handler import cli_command_handler
from ..system.check import check

from .vmware_app import vmware_app
from .vmware_app_cli_options import vmware_app_cli_options

class vmware_app_cli_handler(cli_command_handler):
  'vmware app cli handler.'

  def __init__(self, cli_args):
    super(vmware_app_cli_handler, self).__init__(cli_args, options_class = vmware_app_cli_options)
    check.check_vmware_app_cli_options(self.options)

  def is_installed(self):
    return 0 if vmware_app.is_installed() else 1

  def is_running(self):
    running = vmware_app.is_running()
    if self.options.verbose:
      print(str(running).lower())
    return 0 if running else 1
  
  def ensure_running(self):
    vmware_app.ensure_running()
    return 0

  def ensure_stopped(self):
    vmware_app.ensure_stopped()
    return 0
  
  def install_path(self):
    print(vmware_app.install_path())
    return 0
  
  def vmrun(self):
    print(vmware_app.vmrun_exe_path())
    return 0

  def vmrest(self):
    print(vmware_app.vmrest_exe_path())
    return 0
  
  def ovftool(self):
    print(vmware_app.ovftool_exe_path())
    return 0
  
