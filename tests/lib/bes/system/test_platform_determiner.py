#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.system.detail.platform_determiner_macos import platform_determiner_macos as PDMACOS
from bes.system.detail.platform_determiner_linux_lsb_release import platform_determiner_linux_lsb_release as LINUX_LSB_REL
from bes.system.detail.platform_determiner_linux_os_release import platform_determiner_linux_os_release as LINUX_OS_REL

class test_platform_determiner(unittest.TestCase):

  class fake_macos_platform(object):
    'A fake version of the standard python module platform with enough support for macos unit tests.'
    
    def __init__(self, version, arch):
      self._version = version
      self._arch = arch

    def mac_ver(self):
      return ( self._version, ('', '', ''), self._arch )
      
    def machine(self):
      return self._arch
  
  def test_platform_determiner_macos(self):
    PLAT = self.fake_macos_platform

    self.assertEqual( 'macos', PDMACOS(PLAT('10.13', 'x86_64')).system() )
    self.assertEqual( 'macos', PDMACOS(PLAT('10.13.5', 'x86_64')).system() )
    self.assertEqual( 'x86_64', PDMACOS(PLAT('10.13', 'x86_64')).arch() )
    self.assertEqual( '', PDMACOS(PLAT('10.13', 'x86_64')).distro() )
    self.assertEqual( None, PDMACOS(PLAT('10.13', 'x86_64')).family() )

  class fake_linux_platform(object):

    def __init__(self, arch):
      self._arch = arch

    def machine(self):
      return self._arch

  def test_linux_lsb_release_ubuntu_16(self):
    PLAT = self.fake_linux_platform

    LSB_RELEASE = '''\
Distributor ID:	Ubuntu
Description:	Ubuntu 16.04.5 LTS
Release:	16.04
Codename:	xenial
'''
    
    self.assertEqual( 'linux', LINUX_LSB_REL(PLAT('x86_64'), LSB_RELEASE).system() )
    self.assertEqual( 'debian', LINUX_LSB_REL(PLAT('x86_64'), LSB_RELEASE).family() )
    self.assertEqual( '16', LINUX_LSB_REL(PLAT('x86_64'), LSB_RELEASE).version_major() )
    self.assertEqual( '04', LINUX_LSB_REL(PLAT('x86_64'), LSB_RELEASE).version_minor() )
    self.assertEqual( 'x86_64', LINUX_LSB_REL(PLAT('x86_64'), LSB_RELEASE).arch() )

    
  def test_linux_lsb_release_raspbian_94(self):
    PLAT = self.fake_linux_platform

    LSB_RELEASE = '''\
Distributor ID: Raspbian
Description:    Raspbian GNU/Linux 9.4 (stretch)
Release:    9.4
Codename:   stretch
'''
    d = LINUX_LSB_REL(PLAT('x86_64'), LSB_RELEASE)
    self.assertEqual( 'linux', LINUX_LSB_REL(PLAT('x86_64'), LSB_RELEASE).system() )
    self.assertEqual( 'debian', LINUX_LSB_REL(PLAT('x86_64'), LSB_RELEASE).family() )
    self.assertEqual( '9', LINUX_LSB_REL(PLAT('x86_64'), LSB_RELEASE).version_major() )
    self.assertEqual( '4', LINUX_LSB_REL(PLAT('x86_64'), LSB_RELEASE).version_minor() )
    self.assertEqual( 'x86_64', LINUX_LSB_REL(PLAT('x86_64'), LSB_RELEASE).arch() )

  def test_linux_os_release_ubuntu_16(self):
    PLAT = self.fake_linux_platform

    OS_RELEASE = '''\
NAME="Ubuntu"
VERSION="16.04.5 LTS (Xenial Xerus)"
ID=ubuntu
ID_LIKE=debian
PRETTY_NAME="Ubuntu 16.04.5 LTS"
VERSION_ID="16.04"
HOME_URL="http://www.ubuntu.com/"
SUPPORT_URL="http://help.ubuntu.com/"
BUG_REPORT_URL="http://bugs.launchpad.net/ubuntu/"
VERSION_CODENAME=xenial
UBUNTU_CODENAME=xenial
'''
    
    self.assertEqual( 'linux', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').system() )
    self.assertEqual( 'ubuntu', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').distro() )
    self.assertEqual( 'debian', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').family() )
    self.assertEqual( '16', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').version_major() )
    self.assertEqual( '04', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').version_minor() )
    self.assertEqual( 'x86_64', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').arch() )

  def test_linux_os_release_centos_7(self):
    PLAT = self.fake_linux_platform

    OS_RELEASE = '''\
NAME="CentOS Linux"
VERSION="7 (Core)"
ID="centos"
ID_LIKE="rhel fedora"
VERSION_ID="7"
PRETTY_NAME="CentOS Linux 7 (Core)"
ANSI_COLOR="0;31"
CPE_NAME="cpe:/o:centos:centos:7"
HOME_URL="https://www.centos.org/"
BUG_REPORT_URL="https://bugs.centos.org/"

CENTOS_MANTISBT_PROJECT="CentOS-7"
CENTOS_MANTISBT_PROJECT_VERSION="7"
REDHAT_SUPPORT_PRODUCT="centos"
REDHAT_SUPPORT_PRODUCT_VERSION="7"
'''
    
    self.assertEqual( 'linux', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').system() )
    self.assertEqual( 'centos', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').distro() )
    self.assertEqual( 'redhat', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').family() )
    self.assertEqual( '7', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').version_major() )
    self.assertEqual( None, LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').version_minor() )
    self.assertEqual( 'x86_64', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').arch() )

if __name__ == '__main__':
  unittest.main()
