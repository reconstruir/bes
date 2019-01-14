#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.execute import execute
from .platform_determiner_base import platform_determiner_base

# sed -nE '/SOFTWARE LICENSE AGREEMENT FOR/s/([A-Za-z]+ ){5}|\\$//gp' /System/Library/CoreServices/Setup\ Assistant.app/Contents/Resources/en.lproj/OSXSoftwareLicense.rtf \macOS Mojave

class platform_determiner_macos(platform_determiner_base):
  'macos platform determiner.'

  def __init__(self, platform):
    self._platform = platform
  
  #@abstractmethod
  def system(self):
    'system.'
    return 'macos'

  #@abstractmethod
  def distro(self):
    'distro.'
    return 'macos'
  
  #@abstractmethod
  def family(self):
    'distro family.'
    return None

  #@abstractmethod
  def distributor(self):
    'the distro distributor.'
    return 'apple'

  CODENAMES = {
    '10.10': 'yosemite',
    '10.11': 'el_capitan',
    '10.12': 'sierra',
    '10.13': 'high_sierra',
    '10.14': 'mojave',
  }
  
  #@abstractmethod
  def codename(self):
    'distro codename.'
    version = self.version()
    try:
      return self.CODENAMES[version]
    except Exception as ex:
      raise RuntimeError('Unknown macos version: %s' % (version))

  #@abstractmethod
  def version(self):
    'distro version.'
    return '.'.join(self._platform.mac_ver()[0].split('.')[0:2])

  #@abstractmethod
  def arch(self):
    'arch.'
    return self._platform.machine()
