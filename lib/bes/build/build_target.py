#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import fnmatch

from bes.system.host import host
from ..system.check import check
from bes.common.dict_util import dict_util
from bes.text.text_replace import text_replace
from bes.common.tuple_util import tuple_util
from bes.common.variable import variable
from bes.system.log import logger
from bes.property.cached_property import cached_property

from .build_arch import build_arch
from .build_level import build_level
from .build_system import build_system

from collections import namedtuple

class build_target(namedtuple('build_target', 'system, distro, distro_version_major, distro_version_minor, arch, level')):

  _log = logger('build_target')
  
  DEFAULT_DISTRO_WINDOWS = ''
  DEFAULT_DISTRO_MACOS = ''
  
  DEFAULT_VERSIONS = {
    host.WINDOWS: {
      DEFAULT_DISTRO_WINDOWS: ( '10', '10' ),
    },
    host.MACOS: {
      DEFAULT_DISTRO_MACOS: ( '10', '0' ),
    },
    host.LINUX: {
      host.DEBIAN: ( '10', '9' ),
      host.FEDORA: ( '34', '0' ),
      host.UBUNTU: ( '20', '04' ),
    },
  }
  DEFAULT_ARCHS = {
    host.WINDOWS: {
      DEFAULT_DISTRO_WINDOWS: ( build_arch.X86_64, ),
    },
    host.MACOS: {
      DEFAULT_DISTRO_MACOS: ( build_arch.X86_64, ),
    },
    host.LINUX: {
      host.DEBIAN: ( build_arch.X86_64, ),
      host.FEDORA: ( build_arch.X86_64, ),
      host.UBUNTU: ( build_arch.X86_64, ),
    },
  }
  
  def __new__(clazz, system, distro, distro_version_major, distro_version_minor, arch, level):
    check.check_string(system)
    check.check_string(distro, allow_none = True)
    check.check_string(distro_version_major, allow_none = True)
    check.check_string(distro_version_minor, allow_none = True)
    check.check_string_seq(arch, allow_none = True)
    check.check_string(level, allow_none = True)
    
    distro = clazz.resolve_distro(distro)
    if system != '*':
      system = build_system.parse_system(system)

    if arch != ( '*', ):
      arch = build_arch.check_arch(arch, system, distro)
      arch = build_arch.determine_arch(arch, system, distro)
    if level != '*':
      level = build_level.parse_level(level)
    if distro_version_major != '*':
      distro_version_major = clazz.resolve_distro_version(distro_version_major)
    if distro_version_minor != '*':
      distro_version_minor = clazz.resolve_distro_version(distro_version_minor)
    if system != host.LINUX and distro not in [ '', '*' ]:
      raise ValueError('distro for \"%s\" should be empty/none instead of \"%s\"' % (system, distro))
    if system == host.LINUX and not distro:
      if distro_version_major:
        raise ValueError('no distro so distro_version_major should be empty/none instead of: %s' % (distro_version_major))
      if distro_version_minor:
        raise ValueError('no distro so distro_version_minor should be empty/none instead of: %s' % (distro_version_minor))
    return clazz.__bases__[0].__new__(clazz, system, distro, distro_version_major, distro_version_minor, arch, level)

  def __str__(self):
    return self.build_path
  
  @cached_property
  def build_path(self):
    return self.make_build_path(delimiter = '/')

  @cached_property
  def distro_version(self):
    if not self.distro_version_major:
      return None
    parts = [ self.distro_version_major ]
    if self.distro_version_minor:
      parts.append(self.distro_version_minor)
    return '.'.join(parts)

  @classmethod
  def _arch_to_string(clazz, arch):
    return build_arch.join(arch, delimiter = '-')

  def make_build_path(self, delimiter = '/', include_level = True, include_minor_version = True, include_arch = True):
    system_parts = [ self.system ]
    if self.distro and self.distro != self.system:
      system_parts += [ self.distro ]
    version_parts = []
    if self.distro_version_major:
      version_parts.append(self.distro_version_major)
    if include_minor_version and self.distro_version_minor:
      version_parts.append(self.distro_version_minor)
    version = '.'.join(version_parts)
    if version:
      system_parts += [ version ]
    system_path = '-'.join(system_parts)
    parts = [ system_path ]
    if include_arch:
      parts.append(self._arch_to_string(self.arch))
    if include_level:
      parts.append(self.level)
    return delimiter.join(parts)

  def is_darwin(self):
    return self.system in [ build_system.MACOS, build_system.IOS ]

  def is_macos(self):
    return self.system == build_system.MACOS

  def is_linux(self):
    return self.system == build_system.LINUX

  def is_desktop(self):
    return build_system.is_desktop(self.system)

  def is_mobile(self):
    return build_system.is_mobile(self.system)

  def to_dict(self):
    return self._asdict()

  @property
  def binary_format(self):
    if self.system == build_system.LINUX:
      return 'elf'
    elif self.system == build_system.LINUX:
      return 'macho'
    else:
      return None

  def parse_expression(self, expression):
    variables = {
      'system': self.system,
      'arch': self._arch_to_string(self.arch),
      'level': self.level,
      'distro': self.distro or 'None',
    }
    dict_util.quote_strings(variables)
    exp_with_vars = variable.substitute(expression, variables)
    constants = {
      'MACOS': 'macos',
      'LINUX': 'linux',
      'RELEASE': 'release',
      'DEBUG': 'debug',
      'RASPBIAN': 'raspbian',
    }
    dict_util.quote_strings(constants)
    exp_with_consts = text_replace.replace(exp_with_vars, constants, word_boundary = True)
    return eval(exp_with_consts)

  @classmethod
  def parse_path(clazz, s, delimiter = '/', arch_delimiter = '-', default_value = None):
    parts = s.split(delimiter)
    num_parts = len(parts)
    if num_parts < 1:
      raise ValueError('Invalid build path: %s' % (s))
    system_string = parts.pop(0)
    system, distro, distro_version_major, distro_version_minor = clazz._parse_system(system_string,
                                                                                     default_value)
    if parts:
      arch_string = parts.pop(0)
      arch = build_arch.split(arch_string, delimiter = arch_delimiter)
    else:
      if default_value == None:
        arch = clazz.DEFAULT_ARCHS[system][distro]
      else:
        arch = ( default_value, )
    if parts:
      level = parts.pop(0)
    else:
      if default_value == None:
        level = build_level.DEFAULT_LEVEL
      else:
        level = default_value
    clazz._log.log_d(f'parse_path: system="{system}" distro="{distro}" distro_version_major="{distro_version_major}" distro_version_minor="{distro_version_minor}"')
    result = build_target(system, distro, distro_version_major, distro_version_minor, arch, level)
    clazz._log.log_d('parse_path: result={}'.format(result))
    return result

  @classmethod
  def _parse_system(clazz, s, default_value):
    parts = s.split('-')
    clazz._log.log_d(f'_parse_system: s="{s}" default_value="{default_value}" parts="{parts}"')
    if len(parts) < 1:
      raise ValueError('Invalid system: {}'.format(s))
    distro = ''
    distro_version_major = default_value
    distro_version_minor = default_value
    system = parts.pop(0)

    if len(parts) == 2:
      distro = parts.pop(0)

    if parts:
      distro_version_major, distro_version_minor = clazz._parse_version(parts.pop(0), default_value)
    if parts:
      raise ValueError('Invalid system: {}'.format(s))
    
    return system, distro, distro_version_major, distro_version_minor

  @classmethod
  def _parse_version(clazz, s, default_value):
    clazz._log.log_d(f'_parse_version: s={s} default_value={default_value}')
    if not s:
      return ( default_value, default_value )
    parts = s.split('.')
    assert len(parts) >= 1
    distro_version_major = parts.pop(0)
    if parts:
      distro_version_minor = parts.pop(0)
    else:
      distro_version_minor = default_value
    clazz._log.log_d(f'_parse_version: distro_version_major={distro_version_major} distro_version_minor={distro_version_minor}')
    return distro_version_major, distro_version_minor
  
  @classmethod
  def make_host_build_target(clazz, level = build_level.RELEASE):
    if host.SYSTEM == host.LINUX:
      return build_target(host.SYSTEM, host.DISTRO, host.VERSION_MAJOR, None, ( host.ARCH, ), level)
    elif host.SYSTEM == host.MACOS:
      return build_target(host.SYSTEM, None, host.VERSION_MAJOR, None, ( host.ARCH, ), level)
    elif host.SYSTEM == host.WINDOWS:
      return build_target(host.SYSTEM, None, host.VERSION_MAJOR, None, ( host.ARCH, ), level)
    else:
      return build_target(host.SYSTEM, None, host.VERSION_MAJOR, host.VERSION_MINOR, ( host.ARCH, ), level)
      
  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)

  @classmethod
  def resolve_distro_version(clazz, version):
    if check.is_string(version):
      if version.lower() == 'none':
        version = None
    elif version is None:
      version = None
    return version
  
  @classmethod
  def resolve_distro(clazz, distro):
    if check.is_string(distro):
      if distro.lower() == 'none':
        distro = ''
    elif distro is None:
      distro = ''
    return distro

  def match(self, other):
    'Return True if this build target matches text'
    check.check_build_target(other)

    self._log.log_d(f'match: self={self} other={other}')
    if not fnmatch.fnmatch(self.system, other.system):
      return False
    if not fnmatch.fnmatch(self.distro, other.distro):
      return False
    if not fnmatch.fnmatch(self.distro_version, other.distro_version):
      return False
    if not fnmatch.fnmatch(self.distro_version_minor, other.distro_version_minor):
      return False
    if not fnmatch.fnmatch(self.level, other.level):
      return False
    if len(other.arch) != 1:
      raise ValueError('arch should be just one arch or wildcard: {}'.format(other.arch))
    for arch in self.arch:
      if fnmatch.fnmatch(arch, other.arch[0]):
        return True
    return False

  def match_text(self, text, delimiter = '/', arch_delimiter = '-'):
    'Return True if this build target matches text'
    check.check_string(text)

    other = self.parse_path(text, delimiter = delimiter, arch_delimiter = arch_delimiter, default_value = '*')
    return self.match(other)
  
check.register_class(build_target)
