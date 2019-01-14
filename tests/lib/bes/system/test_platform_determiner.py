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

    self.assertEqual( 'yosemite', PDMACOS(PLAT('10.10.1', 'x86_64')).codename() )
    self.assertEqual( 'el_capitan', PDMACOS(PLAT('10.11.1', 'x86_64')).codename() )
    self.assertEqual( 'sierra', PDMACOS(PLAT('10.12.1', 'x86_64')).codename() )
    self.assertEqual( 'high_sierra', PDMACOS(PLAT('10.13.5', 'x86_64')).codename() )

    self.assertEqual( 'x86_64', PDMACOS(PLAT('10.13', 'x86_64')).arch() )

    self.assertEqual( 'macos', PDMACOS(PLAT('10.13', 'x86_64')).distro() )
    self.assertEqual( None, PDMACOS(PLAT('10.13', 'x86_64')).family() )

  class fake_linux_platform(object):

    def __init__(self, arch):
      self._arch = arch

    def machine(self):
      return self._arch
    
  def test_platform_determiner_linux_lsb(self):
    PLAT = self.fake_linux_platform

    UBUNTU_16_04_LSB_RELEASE = '''Distributor ID:	Ubuntu
Description:	Ubuntu 16.04.5 LTS
Release:	16.04
Codename:	xenial
'''
    
    self.assertEqual( 'linux', LINUX_LSB_REL(PLAT('x86_64'), UBUNTU_16_04_LSB_RELEASE).system() )
    self.assertEqual( 'xenial', LINUX_LSB_REL(PLAT('x86_64'), UBUNTU_16_04_LSB_RELEASE).codename() )
    self.assertEqual( 'debian', LINUX_LSB_REL(PLAT('x86_64'), UBUNTU_16_04_LSB_RELEASE).family() )
    self.assertEqual( '16', LINUX_LSB_REL(PLAT('x86_64'), UBUNTU_16_04_LSB_RELEASE).version() )
    self.assertEqual( 'ubuntu', LINUX_LSB_REL(PLAT('x86_64'), UBUNTU_16_04_LSB_RELEASE).distributor() )
    self.assertEqual( 'x86_64', LINUX_LSB_REL(PLAT('x86_64'), UBUNTU_16_04_LSB_RELEASE).arch() )

    RASPBIAN_9_4_LSB_RELEASE = '''Distributor ID: Raspbian
Description:    Raspbian GNU/Linux 9.4 (stretch)
Release:    9.4
Codename:   stretch
'''
    d = LINUX_LSB_REL(PLAT('x86_64'), RASPBIAN_9_4_LSB_RELEASE)
    self.assertEqual( 'linux', LINUX_LSB_REL(PLAT('x86_64'), RASPBIAN_9_4_LSB_RELEASE).system() )
    self.assertEqual( 'stretch', LINUX_LSB_REL(PLAT('x86_64'), RASPBIAN_9_4_LSB_RELEASE).codename() )
    self.assertEqual( 'debian', LINUX_LSB_REL(PLAT('x86_64'), RASPBIAN_9_4_LSB_RELEASE).family() )
    self.assertEqual( '9', LINUX_LSB_REL(PLAT('x86_64'), RASPBIAN_9_4_LSB_RELEASE).version() )
    self.assertEqual( 'raspbian', LINUX_LSB_REL(PLAT('x86_64'), RASPBIAN_9_4_LSB_RELEASE).distributor() )
    self.assertEqual( 'x86_64', LINUX_LSB_REL(PLAT('x86_64'), RASPBIAN_9_4_LSB_RELEASE).arch() )

  def test_platform_determiner_linux_os(self):
    PLAT = self.fake_linux_platform

    UBUNTU_16_04_OS_RELEASE = '''\
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
    
    self.assertEqual( 'linux', LINUX_OS_REL(PLAT('x86_64'), UBUNTU_16_04_OS_RELEASE, '<unittest>').system() )
    self.assertEqual( 'debian', LINUX_OS_REL(PLAT('x86_64'), UBUNTU_16_04_OS_RELEASE, '<unittest>').family() )
    self.assertEqual( '16', LINUX_OS_REL(PLAT('x86_64'), UBUNTU_16_04_OS_RELEASE, '<unittest>').version() )
    self.assertEqual( 'ubuntu', LINUX_OS_REL(PLAT('x86_64'), UBUNTU_16_04_OS_RELEASE, '<unittest>').distributor() )
    self.assertEqual( 'x86_64', LINUX_OS_REL(PLAT('x86_64'), UBUNTU_16_04_OS_RELEASE, '<unittest>').arch() )

    return
    RASPBIAN_9_4_LSB_RELEASE = '''Distributor ID: Raspbian
Description:    Raspbian GNU/Linux 9.4 (stretch)
Release:    9.4
Codename:   stretch
'''
    d = LINUX_OS_REL(PLAT('x86_64'), RASPBIAN_9_4_LSB_RELEASE)
    self.assertEqual( 'linux', LINUX_OS_REL(PLAT('x86_64'), RASPBIAN_9_4_LSB_RELEASE).system() )
    self.assertEqual( 'stretch', LINUX_OS_REL(PLAT('x86_64'), RASPBIAN_9_4_LSB_RELEASE).codename() )
    self.assertEqual( 'debian', LINUX_OS_REL(PLAT('x86_64'), RASPBIAN_9_4_LSB_RELEASE).family() )
    self.assertEqual( '9', LINUX_OS_REL(PLAT('x86_64'), RASPBIAN_9_4_LSB_RELEASE).version() )
    self.assertEqual( 'raspbian', LINUX_OS_REL(PLAT('x86_64'), RASPBIAN_9_4_LSB_RELEASE).distributor() )
    self.assertEqual( 'x86_64', LINUX_OS_REL(PLAT('x86_64'), RASPBIAN_9_4_LSB_RELEASE).arch() )
    
    
if __name__ == '__main__':
  unittest.main()
