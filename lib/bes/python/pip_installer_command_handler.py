#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.system.check import check

from .pip_installer import pip_installer
from .pip_installer_options import pip_installer_options

class pip_installer_command_handler(bcli_command_handler):

  def name(self):
    return 'pip_installer'

  def _make_options(self, options, name=None):
    return pip_installer_options(verbose=options.verbose,
                                 debug=options.debug,
                                 root_dir=options.root_dir,
                                 python_exe=options.python_exe,
                                 name=name)

  def _command_install(self, pip_version, name, clobber_install_dir, options):
    check.check_string(pip_version)

    installer = pip_installer(self._make_options(options, name=name))
    installer.install(pip_version, clobber_install_dir)
    return 0

  def _command_update(self, pip_version, name, options):
    check.check_string(pip_version)

    installer = pip_installer(self._make_options(options, name=name))
    installer.update(pip_version)
    return 0

  def _command_uninstall(self, name, options):
    installer = pip_installer(self._make_options(options, name=name))
    installer.uninstall()
    return 0
