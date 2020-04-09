#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .host_info import host_info
from .platform_determiner import platform_determiner

from .compat import with_metaclass

class _host_info_holder(type):
  
  _VALID_KEYS = [ 'ARCH', 'DISTRO', 'FAMILY', 'SYSTEM', 'VERSION_MAJOR', 'VERSION_MINOR' ]
  
  def __getattr__(clazz, key):
    if not key in clazz._VALID_KEYS:
      raise AttributeError('Invalid key: "{}" - should be one of {}'.format(key, ' '.join(clazz._VALID_KEYS)))
    if not hasattr(clazz, 'HOST_INFO'):
      raise AttributeError('_host_info_holder has not be initialized yet.')
    return getattr(clazz.HOST_INFO, key.lower())

class host(with_metaclass(_host_info_holder, object)):

  # systems
  LINUX = 'linux'
  MACOS = 'macos'
  WINDOWS = 'windows'

  SYSTEMS = [ LINUX, MACOS, WINDOWS ]

  # distros
  RASPBIAN = 'raspbian'
  UBUNTU = 'ubuntu'

  DISTROS = [ RASPBIAN, UBUNTU ]

  # families
  FAMILY_DEBIAN = 'debian'
  FAMILY_REDHAT = 'redhat'

  FAMILIES = [ FAMILY_DEBIAN, FAMILY_REDHAT ]

  @classmethod
  def init(clazz):
    determiner = platform_determiner()
    clazz.HOST_INFO = host_info(determiner.system(),
                                determiner.version_major(),
                                determiner.version_minor(),
                                determiner.arch(),
                                determiner.distro(),
                                determiner.family())
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
    raise RuntimeError('unsupported system: {}'.format(system))
  
host.init()

