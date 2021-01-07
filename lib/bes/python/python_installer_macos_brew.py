#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

from bes.unix.brew.brew import brew
#from bes.unix.sudo.sudo_cli_options import sudo_cli_options

from .python_error import python_error
from .python_exe import python_exe
from .python_installer_base import python_installer_base

class python_installer_macos_brew(python_installer_base):
  'Python installer for macos from python.org'
  
  def __init__(self, blurber):
    if not brew.has_brew():
      raise python_error('Please install brew first.')
    super(python_installer_macos_brew, self).__init__(blurber)

  #@abstractmethod
  def available_versions(self, num):
    'Return a list of python versions available to install.'
    check.check_int(num)

    return self._filter_python_packages(brew.available())
    
  #@abstractmethod
  def installed_versions(self):
    'Return a list of installed python versions.'
    return self._filter_python_packages(brew.installed())
    
  #@abstractmethod
  def install(self, full_version):
    'Install the major.minor.revision full version of python.'
    check.check_string(full_version)

    brew.install(full_version)
        
  #@abstractmethod
  def uninstall(self, version_or_full_version):
    'Uninstall a python by version or full_version.'
    check.check_string(version_or_full_version)
    
    brew.uninstall(version_or_full_version)

  #@abstractmethod
  def _filter_python_packages(self, packages):
    'Filter a list of brew packages so it only contains python packages.'
    return sorted([ p for p in packages if p.startswith('python@') ])
