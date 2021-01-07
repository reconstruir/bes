#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.Script import Script
from bes.common.check import check
from bes.script.blurber import blurber

from .python_installer import python_installer
from .python_installer_options import python_installer_options

class python_installer_cli_command(cli_command_handler):
  'python installer cli commands.'

  def __init__(self, cli_args):
    super(python_installer_cli_command, self).__init__(cli_args, options_class = python_installer_options)
    check.check_python_installer_options(self.options)
    bl = blurber(Script.name())
    bl.set_verbose(self.options.verbose)
    self.installer = python_installer(self.options.installer_name, bl)
  
  def available(self, num):
    check.check_int(num)

    available = self.installer.available_versions(num)
    for full_version in available:
      print(full_version)
    return 0
  
  def install(self, full_version):
    check.check_string(full_version)

    self.installer.install(full_version)
    return 0

  def uninstall(self, full_version):
    check.check_string(full_version)

    self.installer.uninstall(full_version)
    return 0

  def installed(self):
    installed = self.installer.installed_versions()
    for full_version in installed:
      print(full_version)
    return 0
  
  def reinstall(self, full_version):
    check.check_string(full_version)

    self.installer.uninstall(full_version)
    self.installer.install(full_version)
    return 0
