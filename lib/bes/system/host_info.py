#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from .check import check

class host_info(namedtuple('host_info', 'system, version_major, version_minor, arch, distro, family, codename')):

  def __new__(clazz, system, version_major, version_minor, arch, distro, family, codename):
    return clazz.__bases__[0].__new__(clazz, system, version_major, version_minor, arch, distro, family, codename)

  @property
  def version(self):
    return '{}.{}'.format(self.version_major, self.version_minor)

  @property
  def triple(self):
    parts = [ self.system, self.distro, self.version_major, self.arch ]
    parts = [ p for p in parts if p ]
    return '-'.join(parts)

  @classmethod
  def parse(clazz, s):
    parts = s.split('-')
    system = parts.pop(0)
    if system in ( 'macos', 'windows' ):
      if not parts:
        raise ValueError('invalid host_info: "{}"'.format(s))
      version = parts.pop(0)
      version_major, _, version_minor = version.partition('.')
      version_minor = version_minor or '0'
      if parts:
        arch = parts.pop(0)
      else:
        arch = 'x86_64'
      distro = ''
      family = None
      codename = None
    else:
      assert False, 'fix for loonix'
    return host_info(system, version_major, version_minor, arch, distro, family, codename)

check.register_class(host_info, include_seq = False)
