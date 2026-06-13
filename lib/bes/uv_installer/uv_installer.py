#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.host import host
from bes.system.log import logger

from . import uv_installer_base
from . import uv_installer_error
from . import uv_installer_linux
from . import uv_installer_macos
from . import uv_installer_windows

class uv_installer(uv_installer_base.uv_installer_base):

  _log = logger('uv_installer')

  _INSTALLER_CLASSES = {
    host.MACOS: uv_installer_macos.uv_installer_macos,
    host.LINUX: uv_installer_linux.uv_installer_linux,
    host.WINDOWS: uv_installer_windows.uv_installer_windows,
  }

  def __init__(self, options):
    check.check_uv_installer_options(options)
    super().__init__(options)

    system = host.SYSTEM
    installer_class = self._INSTALLER_CLASSES.get(system, None)
    if not installer_class:
      raise uv_installer_error.uv_installer_error(f'No uv installer available for system: {system}')
    self._installer = installer_class(options)

  @classmethod
  def available_installers(clazz, system=None):
    'Return a list of installer names for the given system.'
    check.check_string(system, allow_none=True)

    target_system = system or host.SYSTEM
    return [target_system] if target_system in clazz._INSTALLER_CLASSES else []

  def install(self, version=None):
    return self._installer.install(version=version)

  def uninstall(self):
    return self._installer.uninstall()

  def is_installed(self):
    return self._installer.is_installed()

  def installed_version(self):
    return self._installer.installed_version()

  def exe_path(self):
    return self._installer.exe_path()
