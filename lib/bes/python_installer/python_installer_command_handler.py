#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.files.bf_file_ops import bf_file_ops
from bes.system.check import check

from .python_installer import python_installer
from .python_installer_options import python_installer_options

class python_installer_command_handler(bcli_command_handler):

  def name(self):
    return 'python_installer'

  def _make_options(self, options):
    return python_installer_options(verbose=options.verbose,
                                    debug=options.debug,
                                    dry_run=options.dry_run,
                                    installer_name=options.installer_name,
                                    system=options.system)

  def _make_installer(self, options):
    return python_installer(self._make_options(options))

  def _command_installers(self, options):
    installers = python_installer.available_installers(options.system)
    for installer in installers:
      print(installer)
    return 0

  def _command_installed(self, options):
    installed = self._make_installer(options).installed_versions()
    for full_version in installed:
      print(full_version)
    return 0

  def _command_available(self, num, options):
    check.check_int(num)

    available = self._make_installer(options).available_versions(num)
    for full_version in available:
      print(full_version)
    return 0

  def _command_install(self, version, options):
    check.check_string(version)

    self._make_installer(options).install(version)
    return 0

  def _command_update(self, version, options):
    check.check_string(version)

    installer = self._make_installer(options)
    if not installer.needs_update(version):
      print('does not need update: {}'.format(version))
      return 0
    installer.update(version)
    return 0

  def _command_needs_update(self, version, options):
    check.check_string(version)

    installer = self._make_installer(options)
    if not installer.is_installed(version):
      result = True
    else:
      result = installer.needs_update(version)
    return self.handle_boolean_result(result, options.verbose)

  def _command_install_package(self, package_filename, options):
    check.check_string(package_filename)

    self._make_installer(options).install_package(package_filename)
    return 0

  def _command_uninstall(self, version, options):
    check.check_string(version)

    self._make_installer(options).uninstall(version)
    return 0

  def _command_reinstall(self, version, options):
    check.check_string(version)

    installer = self._make_installer(options)
    if installer.is_installed(version):
      installer.uninstall(version)
    installer.install(version)
    return 0

  def _command_download(self, full_version, output_filename, options):
    check.check_string(full_version)
    check.check_string(output_filename, allow_none=True)

    installer = self._make_installer(options)
    tmp_package = installer.download(full_version)
    output_filename = output_filename or path.basename(tmp_package)
    bf_file_ops.rename(tmp_package, output_filename)
    return 0

  def _command_is_installed(self, version, options):
    check.check_string(version)

    return self.handle_boolean_result(self._make_installer(options).is_installed(version),
                                      options.verbose)
