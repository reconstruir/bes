#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.cli.cli_command_handler import cli_command_handler
from ..system.check import check

from .pip_error import pip_error
from .pip_installer import pip_installer
from .pip_installer_options import pip_installer_options

class pip_installer_cli_handler(cli_command_handler):
  'pip installer cli handler.'

  def __init__(self, cli_args):
    super(pip_installer_cli_handler, self).__init__(cli_args, options_class = pip_installer_options)
    check.check_pip_installer_options(self.options)
    self.options.blurber.set_verbose(self.options.verbose)
    self._installer = pip_installer(self.options)

  def install(self, pip_version, clobber_install_dir):
    check.check_string(pip_version)

    self._installer.install(pip_version, clobber_install_dir)
    return 0
    
  def update(self, pip_version):
    check.check_string(pip_version)

    self._installer.update(pip_version)
    return 0

  def uninstall(self):
    check.check_string()

    self._installer.uninstall()
    return 0
