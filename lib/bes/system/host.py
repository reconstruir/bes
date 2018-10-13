#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .host_info import host_info
from .platform_db import platform_determiner

class host(object):

  # systems
  LINUX = 'linux'
  MACOS = 'macos'

  SYSTEMS = [ LINUX, MACOS ]

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
    clazz.SYSTEM = determiner.system()
    clazz.DISTRO = determiner.distro()
    clazz.FAMILY = determiner.family()
    clazz.DISTRIBUTOR = determiner.distributor()
    clazz.VERSION = determiner.version()
    clazz.CODENAME = determiner.codename()
    clazz.ARCH = determiner.arch()
    clazz.HOST_INFO = host_info(clazz.SYSTEM, clazz.VERSION, clazz.ARCH, clazz.DISTRO,
                                clazz.FAMILY, clazz.DISTRIBUTOR, clazz.CODENAME)
    del clazz.init
    
  @classmethod
  def is_macos(clazz):
    'Return True if current system is MACOS'
    return clazz.SYSTEM == clazz.MACOS
    
  @classmethod
  def is_linux(clazz):
    'Return True if current system is LINUX'
    return clazz.SYSTEM == clazz.LINUX
    
host.init()

