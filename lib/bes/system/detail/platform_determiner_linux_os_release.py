#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.execute import execute

from .platform_determiner_base import platform_determiner_base
from .linux_os_release import linux_os_release
from .linux_arch import linux_arch

class platform_determiner_linux_os_release(platform_determiner_base):
  'linux platform determiner that uses /etc/os-release'

  def __init__(self, platform, os_release, filename):
    self._platform = platform
    self._os_release = linux_os_release.parse_os_release(os_release, filename)

  #@abstractmethod
  def system(self):
    'system.'
    return 'linux'

  #@abstractmethod
  def distro(self):
    'distro.'
    return self._os_release.distro

  #@abstractmethod
  def family(self):
    'distro family.'
    return self._os_release.family

  #@abstractmethod
  def distributor(self):
    'the distro distributor.'
    return 'dunno'
  
  #@abstractmethod
  def codename(self):
    'distro codename.'
    return 'dunno'

  #@abstractmethod
  def version_major(self):
    'distro version major.'
    return self._os_release.version_major

  #@abstractmethod
  def version_minor(self):
    'distro version minor.'
    return self._os_release.version_minor
  
  #@abstractmethod
  def arch(self):
    'arch.'
    return linux_arch.arch(self._platform)
