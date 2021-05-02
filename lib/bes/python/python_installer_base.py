#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from collections import namedtuple

from bes.common.check import check
from bes.system.compat import with_metaclass
from bes.script.blurber import blurber

from .python_installer_options import python_installer_options

class python_installer_base(with_metaclass(ABCMeta, object)):

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
    
