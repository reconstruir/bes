#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

from bes.unix.brew.brew import brew
from bes.unix.brew.brew_options import brew_options

from .python_error import python_error
from .python_exe import python_exe
from .python_installer_base import python_installer_base
from .python_python_dot_org import python_python_dot_org

class python_installer_macos_brew(python_installer_base):
  'Python installer for macos from python.org'
  
  def __init__(self, options):
    check.check_python_installer_options(options)

    if not brew.has_brew():
      raise python_error('Please install brew first.')
    super(python_installer_macos_brew, self).__init__(options)
    bo = brew_options(verbose = options.verbose, blurber = options.blurber)
    self._brew = brew(options = bo)

  #@abstractmethod
  def available_versions(self, num):
    'Return a list of python versions available to install.'
    check.check_int(num)
    return python_python_dot_org.available_versions('macos', num)
    
  #@abstractmethod
  def installed_versions(self):
    'Return a list of installed python versions.'
    brew_packages = self._brew.installed()
    return self._filter_python_packages(brew_packages)
    
  #@abstractmethod
  def install(self, full_version):
    'Install the major.minor.revision full version of python.'
    check.check_string(full_version)

    self._brew.install(full_version)

  #@abstractmethod
  def install_package(self, package_filename):
    'Install a python package directly.  Not always supported.'
    raise python_error('direct package installation not supported.')
    
  #@abstractmethod
  def uninstall(self, version_or_full_version):
    'Uninstall a python by version or full_version.'
    check.check_string(version_or_full_version)
    
    self._brew.uninstall(version_or_full_version)

  #@abstractmethod
  def download(self, full_version):
    'Download the major.minor.revision full version of python to a temporary file.'
    raise python_error('download not supported.')
    
  def _filter_python_packages(self, packages):
    'Filter a list of brew packages so it only contains python packages.'
    return sorted([ p for p in packages if p.startswith('python@') ])
