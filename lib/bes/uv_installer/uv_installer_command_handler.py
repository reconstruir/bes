#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.system.check import check

from . import uv_installer
from . import uv_installer_options

class uv_installer_command_handler(bcli_command_handler):

  def name(self):
    return 'uv_installer'

  def _make_options(self, options):
    return uv_installer_options.uv_installer_options(
      verbose=options.verbose,
      dry_run=options.dry_run,
      install_dir=options.install_dir,
      install_script=options.install_script,
      version=options.version,
    )

  def _make_installer(self, options):
    return uv_installer.uv_installer(self._make_options(options))

  def _command_install(self, version, options):
    check.check_string(version, allow_none=True)

    installer_options = self._make_options(options)
    if version:
      installer_options = uv_installer_options.uv_installer_options(
        verbose=options.verbose,
        dry_run=options.dry_run,
        install_dir=options.install_dir,
        install_script=options.install_script,
        version=version,
      )
    uv_installer.uv_installer(installer_options).install(version=version)
    return 0

  def _command_uninstall(self, options):
    self._make_installer(options).uninstall()
    return 0

  def _command_is_installed(self, options):
    return self.handle_boolean_result(self._make_installer(options).is_installed(), options.verbose)

  def _command_installed_version(self, options):
    version = self._make_installer(options).installed_version()
    if version:
      print(version)
    return 0

  def _command_exe_path(self, options):
    exe = self._make_installer(options).exe_path()
    if exe:
      print(exe)
    return 0
