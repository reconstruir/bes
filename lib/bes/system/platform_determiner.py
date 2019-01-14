#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import platform

from .detail.platform_determiner_base import platform_determiner_base

class platform_determiner(platform_determiner_base):

  def __init__(self):
    self._impl = None
    system = platform.system()
    if system == 'Linux':
      from .detail.platform_determiner_linux import platform_determiner_linux
      self._impl = platform_determiner_linux(platform)
    elif system == 'Darwin':
      from .detail.platform_determiner_macos import platform_determiner_macos
      self._impl = platform_determiner_macos(platform)
    if not self._impl:
      raise RuntimeError('Unknown system: %s' % (system))
    
  #@abstractmethod
  def system(self):
    'system.'
    return self._impl.system()

  #@abstractmethod
  def distro(self):
    'distro.'
    return self._impl.distro()
  
  #@abstractmethod
  def family(self):
    'distro family.'
    return self._impl.family()

  #@abstractmethod
  def distributor(self):
    'the distro distributor.'
    return self._impl.distributor()
  
  #@abstractmethod
  def codename(self):
    'distro codename.'
    return self._impl.codename()

  #@abstractmethod
  def version(self):
    'distro version.'
    return self._impl.version()

  #@abstractmethod
  def arch(self):
    'arch.'
    return self._impl.arch()
