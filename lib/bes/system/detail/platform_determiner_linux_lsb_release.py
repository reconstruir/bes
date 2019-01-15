#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .platform_determiner_base import platform_determiner_base

class platform_determiner_linux_lsb_release(platform_determiner_base):
  'linux platform determiner that uses lsb_release -v -a'

  def __init__(self, platform, lsb_release):
    self._platform = platform
    parsed_lsb_release = self._parse_lsb_release(lsb_release)
    self._distro = parsed_lsb_release.get('Distributor ID', None).lower()
    if not self._distro:
      raise RuntimeError('lsb_release missing valid "Distributor ID"')
    self._codename = parsed_lsb_release.get('Codename', None).lower()
    if not self._codename:
      raise RuntimeError('lsb_release missing valid "Codename"')
    self._version = parsed_lsb_release.get('Release', None).lower()
    if not self._version:
      raise RuntimeError('lsb_release missing valid "Release"').lower()
    self._version = self._version.split('.')[0]
    self._distributor = parsed_lsb_release.get('Distributor ID', None).lower()
    if not self._distributor:
      raise RuntimeError('lsb_release missing valid "Distributor ID"').lower()
  
  #@abstractmethod
  def system(self):
    'system.'
    return 'linux'

  #@abstractmethod
  def distro(self):
    'distro.'
    return self._distro

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
  def distributor(self):
    'the distro distributor.'
    return self._distributor
  
  #@abstractmethod
  def codename(self):
    'distro codename.'
    return self._codename

  #@abstractmethod
  def version(self):
    'distro version.'
    return self._version

  #@abstractmethod
  def arch(self):
    'arch.'
    arch = self._platform.machine()
    if arch.startswith('armv7'):
      return 'armv7'
    return arch

  @classmethod
  def _parse_lsb_release(clazz, lsb_release):
    result = {}
    lines = lsb_release.strip().split('\n')
    for line in lines:
      parts = line.partition(':')
      if parts[1] != ':':
        raise RuntimeError('Invalid lsb_release entry: "%s"' % (line))
      result[parts[0].strip()] = parts[2].strip()
    return result
