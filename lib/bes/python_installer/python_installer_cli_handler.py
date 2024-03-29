#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.Script import Script
from ..system.check import check
from bes.fs.file_util import file_util
from bes.python.python_version import python_version
from bes.script.blurber import blurber

from .python_installer import python_installer
from .python_installer_options import python_installer_options

class python_installer_cli_handler(cli_command_handler):
  'python installer cli handler.'

  def __init__(self, cli_args):
    super(python_installer_cli_handler, self).__init__(cli_args, options_class = python_installer_options)
    check.check_python_installer_options(self.options)
    self.options.blurber.set_verbose(self.options.verbose)
    self.installer = python_installer(self.options)

  def installers(self):
    installers = python_installer.available_installers(self.options.system)
    for installer in installers:
      print(installer)
    return 0

  def installed(self):
    installed = self.installer.installed_versions()
    for full_version in installed:
      print(full_version)
    return 0
  
  def available(self, num):
    check.check_int(num)

    available = self.installer.available_versions(num)
    for full_version in available:
      print(full_version)
    return 0
  
  def install(self, version):
    check.check_string(version)

    self.installer.install(version)
    return 0

  def update(self, version):
    check.check_string(version)

    if not self.installer.needs_update(version):
      print('does not need update: {}'.format(version))
      return 0
    
    self.installer.update(version)
    return 0

  def needs_update(self, version):
    check.check_string(version)

    if not self.installer.is_installed(version):
      result = True
    else:
      result = self.installer.needs_update(version)
    return self.handle_boolean_result(result, self.options.verbose)
  
  def install_package(self, package_filename):
    check.check_string(package_filename)

    self.installer.install_package(package_filename)
    return 0
  
  def uninstall(self, version):
    check.check_string(version)

    self.installer.uninstall(version)
    return 0

  def reinstall(self, version):
    check.check_string(version)

    if self.is_installed(version):
      self.installer.uninstall(version)
    self.installer.install(version)
    return 0

  def download(self, full_version, output_filename):
    check.check_string(full_version)
    check.check_string(output_filename, allow_none = True)

    tmp_package = self.installer.download(full_version)
    output_filename = output_filename or path.basename(tmp_package)
    file_util.rename(tmp_package, output_filename)
    return 0
  
  def is_installed(self, version):
    check.check_string(version)

    return self.handle_boolean_result(self.installer.is_installed(version),
                                      self.options.verbose)
