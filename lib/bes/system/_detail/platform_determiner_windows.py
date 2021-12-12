#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import platform

from .platform_determiner_base import platform_determiner_base

class platform_determiner_windows(platform_determiner_base):
  'macos platform determiner.'

  def __init__(self, platform):
    self._platform = platform
  
  #@abstractmethod
  def system(self):
    'system.'
    return 'windows'

  #@abstractmethod
  def distro(self):
    'distro.'
    return ''

  #@abstractmethod
  def codename(self):
    'codename.'
    return None
  
  #@abstractmethod
  def family(self):
    'distro family.'
    return None

  #@abstractmethod
  def version_major(self):
    'distro version major number.'
    return platform.version().split('.')[0]

  #@abstractmethod
  def version_minor(self):
    'distro version minor number.'
    return platform.version().split('.')[1]

  _ARCH_MAP = {
    'amd64': 'x86_64',
  }
  #@abstractmethod
  def arch(self):
    'arch.'
    arch = self._platform.machine().lower()
    return self._ARCH_MAP.get(arch, arch)
