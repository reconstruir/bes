#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.system.host import host

from .python_error import python_error
from .python_installer_base import python_installer_base
from .python_installer_macos_brew import python_installer_macos_brew
from .python_installer_macos_python_dot_org import python_installer_macos_python_dot_org
from .python_installer_windows_python_dot_org import python_installer_windows_python_dot_org

class python_installer(python_installer_base):

  _INSTALLER_CLASSES = {
    host.MACOS: {
      'python.org': python_installer_macos_python_dot_org,
      'brew': python_installer_macos_brew,
    },
    host.LINUX: {
    },
    host.WINDOWS: {
      'python.org': python_installer_windows_python_dot_org,
    },
  }

  _DEFAULT_INSTALLER_CLASS = {
    host.MACOS: 'brew',
    host.WINDOWS: 'python.org',
  }
  
  def __init__(self, options):
    check.check_python_installer_options(options)

    options.system = options.system or host.SYSTEM
    host.check_system(options.system)

    super(python_installer, self).__init__(options)
    
    if not options.installer_name:
      default_installer_class_name = self._DEFAULT_INSTALLER_CLASS.get(options.system, None)
      if not default_installer_class_name:
        raise python_error('No default python installer found for this system: {}'.format(options.system))
      options.installer_name = default_installer_class_name
    
    system_installer_classes = self._INSTALLER_CLASSES.get(options.system, None)
    if not system_installer_classes:
      raise python_error('No python installer named "{}" found for system: {}'.format(options.installer_name,
                                                                                      options.system))
    installer_class = system_installer_classes.get(options.installer_name, None)
    if not installer_class:
      raise python_error('No python installer named "{}" found for system: {}'.format(options.installer_name,
                                                                                      options.system))
    self.installer = installer_class(options)

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
  def install_package(self, package_filename):
    'Install a python package directly.  Not always supported.'
    self.installer.install_package(package_filename)
  
  #@abstractmethod
  def uninstall(self, version_or_full_version):
    'Uninstall a python by version or full_version.'
    return self.installer.uninstall(version_or_full_version)

  #@abstractmethod
  def download(self, full_version):
    'Download the major.minor.revision full version of python to a temporary file.'
    return self.installer.download(full_version)
  
check.register_class(python_installer, include_seq = False)
