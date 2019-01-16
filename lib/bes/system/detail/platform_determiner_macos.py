#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.execute import execute
from .platform_determiner_base import platform_determiner_base

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
  def version(self):
    'distro version.'
    return '.'.join(self._platform.mac_ver()[0].split('.')[0])

  #@abstractmethod
  def version_major(self):
    'distro version major number.'
    return self._platform.mac_ver()[0].split('.')[0]

  #@abstractmethod
  def version_minor(self):
    'distro version minor number.'
    return self._platform.mac_ver()[0].split('.')[1]
  
  #@abstractmethod
  def arch(self):
    'arch.'
    return self._platform.machine()
