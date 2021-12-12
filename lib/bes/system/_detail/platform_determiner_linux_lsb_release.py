#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .platform_determiner_base import platform_determiner_base
from .linux_os_release import linux_os_release
from .linux_lsb_release import linux_lsb_release

class platform_determiner_linux_lsb_release(platform_determiner_base):
  'linux platform determiner that uses lsb_release -v -a'

  def __init__(self, platform, lsb_release):
    self._platform = platform
    parsed_lsb_release = linux_lsb_release.parse_lsb_release(lsb_release)
    self._distro = parsed_lsb_release.get('Distributor ID', None).lower()
    if not self._distro:
      raise RuntimeError('lsb_release missing valid "Distributor ID"')
    self._version_major, self._version_minor = linux_os_release.parse_version_major_minor(parsed_lsb_release.get('Release', ''))
    if not self._version_major:
      raise RuntimeError('lsb_release missing valid "Release"').lower()
    self._codename = parsed_lsb_release.get('Codename', None).lower()
  
  #@abstractmethod
  def system(self):
    'system.'
    return 'linux'

  #@abstractmethod
  def distro(self):
    'distro.'
    return self._distro

  #@abstractmethod
  def codename(self):
    'codename.'
    return self._codename
  
  FAMILIES = {
    'debian': 'debian',
    'ubuntu': 'debian',
    'raspbian': 'debian',
    'mint': 'debian',
    'arch': 'arch',
    'fedora': 'redhat',
    'redhat': 'redhat',
  }
  
  #@abstractmethod
  def family(self):
    'distro family.'
    distro = self.distro()
    try:
      return self.FAMILIES[distro]
    except Exception as ex:
      raise RuntimeError('Unknown linux distro: %s' % (distro))
    return None

  #@abstractmethod
  def version_major(self):
    'distro version major.'
    return self._version_major

  #@abstractmethod
  def version_minor(self):
    'distro version minor.'
    return self._version_minor
  
  #@abstractmethod
  def arch(self):
    'arch.'
    arch = self._platform.machine()
    if arch.startswith('armv7'):
      return 'armv7'
    return arch
