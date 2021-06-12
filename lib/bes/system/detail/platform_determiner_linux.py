#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import subprocess

from .platform_determiner_base import platform_determiner_base
from .linux_os_release import linux_os_release
from .linux_lsb_release import linux_lsb_release

class platform_determiner_linux(platform_determiner_base):

  def __init__(self, platform):
    impl = self._make_impl(platform)
    if not impl:
      raise RuntimeError('Unknown linux system: %s - %s' % (str(platform)))
    self._impl = impl

  @classmethod
  def _make_impl(self, platform):
    if linux_os_release.has_os_release():
      filename, content = linux_os_release.read_os_release()
      from .platform_determiner_linux_os_release import platform_determiner_linux_os_release
      return platform_determiner_linux_os_release(platform, content, filename)
    elif linux_lsb_release.has_lsb_release():
      lsb_release = linux_lsb_release.lsb_release_output()
      return platform_determiner_linux_lsb_release(platform, lsb_release)
    else:
      return None
   
  #@abstractmethod
  def system(self):
    'system.'
    return self._impl.system()

  #@abstractmethod
  def distro(self):
    'distro.'
    return self._impl.distro()

  #@abstractmethod
  def codename(self):
    'codename.'
    return self._impl.codename()
  
  #@abstractmethod
  def family(self):
    'distro family.'
    return self._impl.family()

  #@abstractmethod
  def version_major(self):
    'distro version major.'
    return self._impl.version_major()

  #@abstractmethod
  def version_minor(self):
    'distro version minor.'
    return self._impl.version_minor()

  #@abstractmethod
  def arch(self):
    'arch.'
    return self._impl.arch()
