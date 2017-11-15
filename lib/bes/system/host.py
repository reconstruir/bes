#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re, platform

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

  # distro versions
  _DISTRO_VERSIONS = {
    RASPBIAN: {
      '8': 'jessie',
      '7': 'wheezy',
    },
    UBUNTU: {
      '14.04': 'trusty',
      '16.04': 'xenial',
    },
    MACOS: {
      '10.10': 'yosemite',
      '10.11': 'el_capitan',
      '10.12': 'sierra',
    },
   }

  @classmethod
  def _determine_system(clazz):
    'Determine the current system using the python platorm module.'
    _system = platform.system()
    if _system == 'Linux':
      return 'linux'
    elif _system == 'Darwin':
      return 'macos'
    else:
      raise RuntimeError('Unknown system: %s' % (_system))

  @classmethod
  def _parse_linux_issue(clazz):
    'Parse /etc/issue and return a list of its parts.'
    try:
      with open('/etc/issue', 'r') as fin:
        issue = fin.read().lower()
    except:
      raise RuntimeError('Unknown linux distro: %s' % (platform.platform()))
    parts = [ p for p in re.split('\s+', issue) if p ]
    return [ p.lower() for p in parts if p ]

  @classmethod
  def _determine_distro_version(clazz, distro, tentative_version, known_versions):
    version = None
    codename = None
    for v in known_versions:
      if tentative_version.startswith(v):
        version = v
        codename = known_versions[version]
        break
    if not version:
      raise RuntimeError('Unknown %s version: %s' % (distro, tentative_version))
    return ( version, codename )

  @classmethod
  def _determine_distro_linux(clazz):
    issue = clazz._parse_linux_issue()
    distro = issue[0]
    version = None
    codename = None
    family = None
    if distro == clazz.RASPBIAN:
      version, codename = clazz._determine_distro_version(distro, issue[2], clazz._DISTRO_VERSIONS[distro])
      family = clazz.FAMILY_DEBIAN
    elif distro == clazz.UBUNTU:
      version, codename = clazz._determine_distro_version(distro, issue[1], clazz._DISTRO_VERSIONS[distro])
      family = clazz.FAMILY_DEBIAN
    return ( distro, family, version, codename )

  @classmethod
  def init(clazz):
    clazz.SYSTEM = clazz._determine_system()
    if clazz.SYSTEM == clazz.LINUX:
      clazz.DISTRO, clazz.FAMILY, clazz.VERSION, clazz.CODENAME = clazz._determine_distro_linux()
    elif clazz.SYSTEM == clazz.MACOS:
      clazz.DISTRO = clazz.MACOS
      clazz.VERSION, clazz.CODENAME = clazz._determine_distro_version(clazz.MACOS,
                                                                      platform.mac_ver()[0],
                                                                      clazz._DISTRO_VERSIONS[clazz.MACOS])
      clazz.FAMILY = clazz.MACOS
    else:
      assert False

    assert clazz.SYSTEM
    assert clazz.DISTRO
    assert clazz.FAMILY
    assert clazz.VERSION
    assert clazz.CODENAME
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

