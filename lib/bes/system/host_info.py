#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

class host_info(namedtuple('host_info', 'system, version, arch, distro, family')):

  def __new__(clazz, system, version, arch, distro, family):
    return clazz.__bases__[0].__new__(clazz, system, version, arch, distro, family)

