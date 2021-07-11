#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from os import path
import re

class linux_os_release(object):
  'Parse /etc/os-release'

  OS_RELEASE = '/etc/os-release'
  
  _parse_result = namedtuple('_parse_result', 'distro, version_major, version_minor, family, codename')
  @classmethod
  def parse_os_release(clazz, text, filename):
    'Parse the os-release content and return a namedtuple of the values.'
    lines = [ line.strip() for line in text.split('\n') ]
    values = [ clazz._tokenize_line(line) for line in lines if line ]
    d = dict(values)
    if 'ID' not in d:
      raise ValueError('No ID found in os-release: %s' % (filename))
    distro = clazz._parse_distro(d['ID'])
    if 'VERSION_ID' not in d:
      raise ValueError('No VERSION_ID found in os-release: %s' % (filename))
    version_major, version_minor = clazz._parse_version(distro, d['VERSION_ID'], filename)
    if 'ID_LIKE' in d:
      family = clazz._parse_family(d['ID_LIKE'])
    else:
      family = clazz._guess_family(distro)
    codename = None
    if 'VERSION_CODENAME' in d:
      codename = d['VERSION_CODENAME'].strip().lower()
    elif 'PRETTY_NAME' in d:
      pretty_name = d['PRETTY_NAME'].strip().lower()
      f = re.findall(r'.*\s+\((.+)\).*', pretty_name)
      if f and len(f) == 1:
        codename = f[0].strip()
    return clazz._parse_result(distro, version_major, version_minor, family, codename)

  @classmethod
  def has_os_release(clazz):
    'Return True if /etc/os-release exists.'
    return path.exists(clazz.OS_RELEASE)
  
  @classmethod
  def read_os_release(clazz):
    with open(clazz.OS_RELEASE, 'r') as fin:
      return clazz.OS_RELEASE, fin.read()
    
  @classmethod
  def _tokenize_line(clazz, line):
    line = line.strip()
    if not line:
      return None, None
    key, delimeter, value = line.partition('=')
    if delimeter != '=':
      return None, None
    return ( key.strip(), value.strip() )
  
  @classmethod
  def _parse_version(clazz, distro, version, filename):
    'Parse the version.'
    if not version:
      raise ValueError('Invallid version \"%s\" in os-release: %s' % (version, filename))
    # Some distros like ubuntu will quote their version.  Some like alpine won't
    if version[0] in [ '"', "'" ]:
      version = version[1:]
    if version[-1] in [ '"', "'" ]:
      version = version[0:-1]
    return clazz.parse_version_major_minor(version)
  
  @classmethod
  def _parse_distro(clazz, text):
    'Parse the distro text.'
    return clazz._unquote_text(text)

  @classmethod
  def _unquote_text(clazz, text):
    'Unquote text if quoted.'
    for c in [ '\'', '"' ]:
      if text.startswith(c):
        assert text.endswith(c)
        return text[1:-1]
    return text

  _FAMILY_ALIASES = {
    'rhel fedora': 'redhat',
  }
  
  @classmethod
  def _parse_family(clazz, text):
    'Parse the family text.'
    family = clazz._unquote_text(text)
    return clazz._FAMILY_ALIASES.get(family, family)

  _FAMILY_GUESSES = {
    'alpine': 'alpine',
    'fedora': 'redhat',
  }
  
  @classmethod
  def _guess_family(clazz, distro):
    'Guess the distro family.'
    for pattern, family in clazz._FAMILY_GUESSES.items():
      if pattern in distro:
        return family
    return 'unknown'

  @classmethod
  def arch(clazz, platform):
    'arch.'
    arch = platform.machine()
    if arch.startswith('armv7'):
      return 'armv7'
    return arch
  
  @classmethod
  def parse_version_major_minor(clazz, version):
    version_major = None
    version_minor = None
    version_parts = version.split('.')
    if version_parts:
      version_major = version_parts.pop(0)
    if version_parts:
      version_minor = version_parts.pop(0)
    return version_major, version_minor

  
