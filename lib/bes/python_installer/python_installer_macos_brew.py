#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

from bes.unix.brew.brew import brew
from bes.unix.brew.brew_options import brew_options

from bes.python.python_exe import python_exe
from bes.python.python_version import python_version

from .python_installer_error import python_installer_error
from .python_installer_base import python_installer_base
from .python_python_dot_org import python_python_dot_org

class python_installer_macos_brew(python_installer_base):
  'Python installer for macos from python.org'
  
  def __init__(self, options):
    check.check_python_installer_options(options)

    if not brew.has_brew():
      raise python_installer_error('Please install brew first.')
    super(python_installer_macos_brew, self).__init__(options)
    bo = brew_options(verbose = options.verbose, blurber = options.blurber)
    self._brew = brew(options = bo)

  #@abstractmethod
  def available_versions(self, num):
    'Return a list of python versions available to install.'
    check.check_int(num)

    return self._filter_python_packages(self._brew.available())
    
  #@abstractmethod
  def installed_versions(self):
    'Return a list of installed python versions.'
    return self._filter_python_packages(self._brew.installed())

  #@abstractmethod
  def install(self, version):
    'Install the major.minor.revision or major.minor version of python.'
    v = python_version.check_version_or_full_version(version)
    if v.is_full_version():
      raise python_installer_error('Install by full_version not supported by this installer.')
    assert v.is_version()
    self._brew.install(version)

  #@abstractmethod
  def update(self, version):
    'Update to the latest major.minor version of python.'
    python_version.check_version(version)
    assert False
    
  #@abstractmethod
  def install_package(self, package_filename):
    'Install a python package directly.  Not always supported.'
    raise python_installer_error('Direct package installation not supported by this installer.')
    
  #@abstractmethod
  def uninstall(self, version_or_full_version):
    'Uninstall a python by version or full_version.'
    check.check_string(version_or_full_version)
    
    self._brew.uninstall(version_or_full_version)

  #@abstractmethod
  def download(self, full_version):
    'Download the major.minor.revision full version of python to a temporary file.'
    raise python_installer_error('Download not supported.')

  #@abstractmethod
  def supports_full_version(self):
    'Return True if this installer supports installing by full version.'
    return False
  
  def _filter_python_packages(self, packages):
    'Filter a list of brew packages so it only contains python packages.'
    return sorted([ p for p in packages if p.startswith('python@') ])
