#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

#    ( 'linux', 'debian', 'ubuntu',   'xenial',      '16.04', [ 'i386', 'x86_64' ] ),

class host_info(namedtuple('host_info', 'system, version, arch, distro, distro_family, codename')):

  def __new__(clazz, system, version, arch, distro = None, distro_family = None, codename = None):
    return clazz.__bases__[0].__new__(clazz, system, version, arch, distro, distro_family, codename)

