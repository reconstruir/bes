#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import platform
from collections import namedtuple

from abc import abstractmethod, ABCMeta
from .compat import with_metaclass
from .execute import execute

class _platform_determiner_base(with_metaclass(ABCMeta, object)):
  'Abstract base class for determining what platform we are on.'
  
  @abstractmethod
  def system(self):
    'system.'
    pass

  @abstractmethod
  def distro(self):
    'distro.'
    pass
  
  @abstractmethod
  def family(self):
    'distro family.'
    pass

  @abstractmethod
  def distributor(self):
    'the distro distributor.'
    pass

  @abstractmethod
  def codename(self):
    'distro codename.'
    pass

  @abstractmethod
  def version(self):
    'distro version.'
    pass

  @abstractmethod
  def arch(self):
    'arch.'
    pass

class _platform_determiner_macos(_platform_determiner_base):
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
    return None
  
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

class _platform_determiner_linux(_platform_determiner_base):
  'linux platform determiner.'

  def __init__(self, platform, lsb_release):
    self._platform = platform
    parsed_lsb_release = self.parse_lsb_release(lsb_release)
    self._distro = parsed_lsb_release.get('Distributor ID', None).lower()
    if not self._distro:
      raise RuntimeError('lsb_release missing valid "Distributor ID"')
    self._codename = parsed_lsb_release.get('Codename', None).lower()
    if not self._codename:
      raise RuntimeError('lsb_release missing valid "Codename"')
    self._version = parsed_lsb_release.get('Release', None).lower()
    if not self._version:
      raise RuntimeError('lsb_release missing valid "Release"').lower()
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
  def parse_lsb_release(clazz, lsb_release):
    result = {}
    lines = lsb_release.strip().split('\n')
    for line in lines:
      parts = line.partition(':')
      if parts[1] != ':':
        raise RuntimeError('Invalid lsb_release entry: "%s"' % (line))
      result[parts[0].strip()] = parts[2].strip()
    return result

  '''
  # unused for now but might be useful on a linux that doenst follow lsb
  @classmethod
  def read_etc_issue(clazz):
    'Parse /etc/issue and return a list of its parts.'
    try:
      with open('/etc/issue', 'r') as fin:
        issue = fin.read().lower()
    except:
      raise RuntimeError('Unknown linux distro: %s' % (platform.platform()))
    parts = [ p for p in re.split('\s+', issue) if p ]
    return [ p.lower() for p in parts if p ]
  '''
  
class platform_determiner(_platform_determiner_base):

  def __init__(self):
    system = platform.system()
    if system == 'Linux':
      lsb_release = execute.execute('lsb_release -v -a').stdout
      self._impl = _platform_determiner_linux(platform, lsb_release)
    elif system == 'Darwin':
      self._impl = _platform_determiner_macos(platform, )
    else:
      raise RuntimeError('Unknown system: %s' % (_system))

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

#class host_info(namedtuple('host_info', 'system, version, arch, distro, family, distributor, codename')):
  
#class platform_determiner(object):
#
#  DB = [
#    ( 'linux', 'debian', 'ubuntu',   'xenial',      '16.04', [ 'i386', 'x86_64' ] ),
#    ( 'linux', 'debian', 'ubuntu',   'trusty',      '14.04', [ 'i386', 'x86_64' ] ),
#    ( 'linux', 'debian', 'ubuntu',   'bionic',      '18.04', [ 'i386', 'x86_64' ] ),
#
#    ( 'linux', 'debian', 'raspbian', 'wheezy',      '7',     [ 'armv7' ] ),
#    ( 'linux', 'debian', 'raspbian', 'jessie',      '8',     [ 'armv7' ] ),
#    ( 'linux', 'debian', 'raspbian', 'stretch',     '9',     [ 'armv7' ] ),
#    
#    ( 'macos', None,     None,       'yosemite',    '10.10', [ 'x86_64' ] ),
#    ( 'macos', None,     None,       'el_capitan',  '10.11', [ 'x86_64' ] ),
#    ( 'macos', None,     None,       'sierra',      '10.12', [ 'x86_64' ] ),
#    ( 'macos', None,     None,       'high_sierra', '10.13', [ 'x86_64' ] ),
#    
#  ]
#
