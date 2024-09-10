#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from collections import namedtuple

from ..system.check import check
from bes.python.python_version import python_version
from bes.python.python_version_list import python_version_list
from bes.script.blurber import blurber
from bes.system.log import logger

from .python_installer_options import python_installer_options

class python_installer_base(object, metaclass = ABCMeta):

  _log = logger('python_installer')
  
  def __init__(self, options):
    check.check_python_installer_options(options)

    self.options = options
  
  @abstractmethod
  def available_versions(self, num):
    'Return a list of python versions available to install.'
    raise NotImplemented('available_versions')
  
  @abstractmethod
  def installed_versions(self):
    'Return a list of installed python versions.'
    raise NotImplemented('installed_versions')

  @abstractmethod
  def install(self, version):
    'Install the major.minor.revision or major.minor version of python.'
    raise NotImplemented('install')

  @abstractmethod
  def update(self, version):
    'Update to the latest major.minor version of python.'
    raise NotImplemented('update')

  @abstractmethod
  def needs_update(self, version):
    'Return True if python version major.minor needs update.'
    raise NotImplemented('needs_update')
  
  @abstractmethod
  def install_package(self, package_filename):
    'Install a python package directly.  Not always supported.'
    raise NotImplemented('install_package')
  
  @abstractmethod
  def uninstall(self, full_version):
    'Uninstall the major.minor.revision full version of python.'
    raise NotImplemented('uninstall_full_version')

  @abstractmethod
  def download(self, full_version):
    'Download the major.minor.revision full version of python to a temporary file.'
    raise NotImplemented('download')

  @abstractmethod
  def supports_full_version(self):
    'Return True if this installer supports installing by full version.'
    raise NotImplemented('supports_full_version')
  
  def blurb(self, message, output = None, fit = False):
    'Print a blurb'
    self.options.blurber.blurb(message, output = output, fit = fit)

  def blurb_verbose(self, message, output = None, fit = False):
    'Print a blurb but only in verbose mode'
    self.options.blurber.blurb_verbose(message, output = output, fit = fit)
    
  def installed_versions_matching(self, version):
    'Return installed versions matching version only.'
    version = python_version.check_version_or_full_version(version)

    installed_versions = self.installed_versions()
    self._log.log_d('installed_versions_matching: installed_versions: {}'.format(installed_versions.to_string()))

    matching_versions = installed_versions.filter_by_version(version)
    matching_versions.sort()
    self._log.log_d('installed_versions_matching: matching_versions: {}'.format(matching_versions.to_string()))
    return matching_versions
  
  def is_installed(self, version):
    'Return True if a python matching version is installed.'
    version = python_version.check_version_or_full_version(version)
    self._log.log_d('is_installed: version={}'.format(version))
    matching_versions = self.installed_versions_matching(version)
    self._log.log_d('is_installed: matching_versions={}'.format(matching_versions))
    result = len(matching_versions) > 0
    self._log.log_d('is_installed: result={}'.format(result))
    return result
