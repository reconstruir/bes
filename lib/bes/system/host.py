#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .host_info import host_info
from .platform_determiner import platform_determiner


class _host_info_holder(type):
  
  _VALID_KEYS = [ 'ARCH', 'DISTRO', 'FAMILY', 'SYSTEM', 'VERSION_MAJOR', 'VERSION_MINOR', 'CODENAME' ]
  
  def __getattr__(clazz, key):
    if not key in clazz._VALID_KEYS:
      raise AttributeError('Invalid key: "{}" - should be one of {}'.format(key, ' '.join(clazz._VALID_KEYS)))
    if not hasattr(clazz, 'HOST_INFO'):
      raise AttributeError('_host_info_holder has not be initialized yet.')
    return getattr(clazz.HOST_INFO, key.lower())

class host_error(Exception):
  'Exception raised when a host does match an expectation'
  
  def __init__(self, message):
    super(host_error, self).__init__()
    self.message = message

  def __str__(self):
    return self.message
  
class host(object, metaclass = _host_info_holder):

  # systems
  LINUX = 'linux'
  MACOS = 'macos'
  WINDOWS = 'windows'

  SYSTEMS = ( LINUX, MACOS, WINDOWS )

  # distros
  RASPBIAN = 'raspbian'
  UBUNTU = 'ubuntu'
  FEDORA = 'fedora'
  DEBIAN = 'fedora'

  DISTROS = ( RASPBIAN, UBUNTU )

  # families
  FAMILY_DEBIAN = 'debian'
  FAMILY_REDHAT = 'redhat'

  FAMILIES = ( FAMILY_DEBIAN, FAMILY_REDHAT )

  @classmethod
  def init(clazz):
    determiner = platform_determiner()
    clazz.HOST_INFO = host_info(determiner.system(),
                                determiner.version_major(),
                                determiner.version_minor(),
                                determiner.arch(),
                                determiner.distro(),
                                determiner.family(),
                                determiner.codename())
    del clazz.init
    
  @classmethod
  def is_macos(clazz):
    'Return True if current system is MACOS'
    return clazz.SYSTEM == clazz.MACOS
    
  @classmethod
  def is_linux(clazz):
    'Return True if current system is LINUX'
    return clazz.SYSTEM == clazz.LINUX
    
  @classmethod
  def is_windows(clazz):
    'Return True if current system is WINDOWS'
    return clazz.SYSTEM == clazz.WINDOWS

  @classmethod
  def is_unix(clazz):
    'Return True if current system is LINUX or MACOS'
    return clazz.is_linux() or clazz.is_macos()

  @classmethod
  def raise_unsupported_system(clazz, system = None):
    'Raise a RuntimeError about the system being unsupported.  If system is None host.SYSTEM is used.'
    system = system or host.SYSTEM
    raise host_error('unsupported system: "{}"'.format(system))

  @classmethod
  def raise_unsupported_distro(clazz, distro = None):
    'Raise a RuntimeError about the distro being unsupported.  If distro is None host.DISTRO is used.'
    distro = distro or host.DISTRO
    raise host_error('unsupported distro: "{}"'.format(distro))
  
  @classmethod
  def check_is_macos(clazz):
    'Raise host_error if system is not macos.'
    if clazz.SYSTEM != clazz.MACOS:
      raise host_error('not macos')

  @classmethod
  def check_is_linux(clazz):
    'Raise host_error if system is not linux.'
    if clazz.SYSTEM != clazz.LINUX:
      raise host_error('not linux')

  @classmethod
  def check_system(clazz, system):
    'Raise a RuntimeError about the system being unsupported.  If system is None host.SYSTEM is used.'
    if not system in clazz.SYSTEMS:
      clazz.raise_unsupported_system(clazz, system = system)

  @classmethod
  def check_distro(clazz, system, distro):
    'Raise a RuntimeError about the distro being unsupported.  If distro is None host.DISTRO is used.'
    clazz.check_system(system)

    if system != clazz.LINUX:
      raise RuntimeError('distro is only valid when system is linux instead of "{}": "{}'.format(system, distro))

    if not distro:
      raise RuntimeError('invalid distro for {}: "{}'.format(system, distro))
    
    if not distro in clazz.DISTROS:
      clazz.raise_unsupported_distro(clazz, distro = distro)
      
host.init()

