#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.system.host import host

#if host.SYSTEM == 'macos':
#  from .python_installer_macos import python_installer_macos as python_installer
#elif host.SYSTEM == 'linux':
#  from .python_installer_linux import python_installer_linux as python_installer
#else:
#  host.raise_unsupported_system()

from .python_error import python_error
from .python_installer_base import python_installer_base
from .python_installer_macos_python_dot_org import python_installer_macos_python_dot_org

class python_installer(python_installer_base):

  _INSTALLER_CLASSES = {
    host.MACOS: {
      'python.org': python_installer_macos_python_dot_org,
    },
    host.LINUX: {
    },
  }

  _DEFAULT_INSTALLER_CLASS = {
    host.MACOS: 'python.org',
  }
  
  def __init__(self, installer_name, blurber):
    check.check_string(installer_name, allow_none = True)
    
    super(python_installer, self).__init__(blurber)
    if not installer_name:
      default_installer_class_name = self._DEFAULT_INSTALLER_CLASS.get(host.SYSTEM, None)
      if not default_installer_class_name:
        raise python_error('No default python installer found for this system: {}'.format(host.SYSTEM))
      installer_name = default_installer_class_name
    
    system_installer_classes = self._INSTALLER_CLASSES.get(host.SYSTEM, None)
    if not system_installer_classes:
      raise python_error('No python installer named "{}" found for this system: {}'.format(installer_name, host.SYSTEM))
    installer_class = system_installer_classes.get(installer_name, None)
    if not installer_class:
      raise python_error('No python installer named "{}" found for this system: {}'.format(installer_name, host.SYSTEM))
    self.installer = installer_class(blurber)

  @classmethod
  def available_installers(self, system):
    'Return a list of available installers for the given system.'
    check.check_string(system, allow_none = True)

    installers = self._INSTALLER_CLASSES.get(system or host.SYSTEM, {})
    return [ name for name in installers.keys() ]
    
  #@abstractmethod
  def available_versions(self, num):
    'Return a list of python versions available to install.'
    return self.installer.available_versions(num)
    
  #@abstractmethod
  def installed_versions(self):
    'Return a list of installed python versions.'
    return self.installer.installed_versions()
    
  #@abstractmethod
  def install(self, full_version):
    'Install the major.minor.revision full version of python.'
    return self.installer.install(full_version)
        
  #@abstractmethod
  def uninstall(self, version_or_full_version):
    'Uninstall a python by version or full_version.'
    return self.installer.uninstall(version_or_full_version)
  
check.register_class(python_installer, include_seq = False)
