#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple

class linux_os_release(object):
  'Parse /etc/os-release'

  OS_RELEASE = '/etc/os-release'
  
  _parse_result = namedtuple('_parse_result', 'distro, version, family')
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
    version = clazz._parse_version(distro, d['VERSION_ID'], filename)
    if 'ID_LIKE' in d:
      family = clazz._parse_family(d['ID_LIKE'])
    else:
      family = clazz._guess_family(distro)
    return clazz._parse_result(distro, version, family)

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
    return clazz._version_major(version)
  
  @classmethod
  def _version_major(clazz, version):
    'Return just the major part of the version.'
    parts = version.split('.')
    return parts[0]
  
  @classmethod
  def _parse_distro(clazz, text):
    'Parse the distro text.'
    return text
  
  @classmethod
  def _parse_family(clazz, text):
    'Parse the family text.'
    return text
  
  @classmethod
  def _guess_family(clazz, distro):
    'Guess the distro family.'
    if distro in [ 'alpine' ]:
      return 'alpine'
    return 'unknown'

  @classmethod
  def arch(clazz, platform):
    'arch.'
    arch = platform.machine()
    if arch.startswith('armv7'):
      return 'armv7'
    return arch
  
