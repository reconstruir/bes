#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.system._detail.platform_determiner_macos import platform_determiner_macos as PDMACOS
from bes.system._detail.platform_determiner_linux_lsb_release import platform_determiner_linux_lsb_release as LINUX_LSB_REL
from bes.system._detail.platform_determiner_linux_os_release import platform_determiner_linux_os_release as LINUX_OS_REL

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

  def test_linux_os_release_fedora_28(self):
    PLAT = self.fake_linux_platform

    OS_RELEASE = '''\
NAME=Fedora
VERSION="28 (Workstation Edition)"
ID=fedora
VERSION_ID=28
VERSION_CODENAME=""
PLATFORM_ID="platform:f28"
PRETTY_NAME="Fedora 28 (Workstation Edition)"
ANSI_COLOR="0;34"
LOGO=fedora-logo-icon
CPE_NAME="cpe:/o:fedoraproject:fedora:28"
HOME_URL="https://fedoraproject.org/"
SUPPORT_URL="https://fedoraproject.org/wiki/Communicating_and_getting_help"
BUG_REPORT_URL="https://bugzilla.redhat.com/"
REDHAT_BUGZILLA_PRODUCT="Fedora"
REDHAT_BUGZILLA_PRODUCT_VERSION=28
REDHAT_SUPPORT_PRODUCT="Fedora"
REDHAT_SUPPORT_PRODUCT_VERSION=28
PRIVACY_POLICY_URL="https://fedoraproject.org/wiki/Legal:PrivacyPolicy"
VARIANT="Workstation Edition"
VARIANT_ID=workstation
'''
    
    self.assertEqual( 'linux', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').system() )
    self.assertEqual( 'fedora', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').distro() )
    self.assertEqual( 'redhat', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').family() )
    self.assertEqual( '28', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').version_major() )
    self.assertEqual( None, LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').version_minor() )
    self.assertEqual( 'x86_64', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').arch() )

  def test_linux_os_release_fedora_29_container(self):
    PLAT = self.fake_linux_platform

    OS_RELEASE = '''\
NAME=Fedora
VERSION="29 (Container Image)"
ID=fedora
VERSION_ID=29
VERSION_CODENAME=""
PLATFORM_ID="platform:f29"
PRETTY_NAME="Fedora 29 (Container Image)"
ANSI_COLOR="0;34"
LOGO=fedora-logo-icon
CPE_NAME="cpe:/o:fedoraproject:fedora:29"
HOME_URL="https://fedoraproject.org/"
DOCUMENTATION_URL="https://docs.fedoraproject.org/en-US/fedora/f29/system-administrators-guide/"
SUPPORT_URL="https://fedoraproject.org/wiki/Communicating_and_getting_help"
BUG_REPORT_URL="https://bugzilla.redhat.com/"
REDHAT_BUGZILLA_PRODUCT="Fedora"
REDHAT_BUGZILLA_PRODUCT_VERSION=29
REDHAT_SUPPORT_PRODUCT="Fedora"
REDHAT_SUPPORT_PRODUCT_VERSION=29
PRIVACY_POLICY_URL="https://fedoraproject.org/wiki/Legal:PrivacyPolicy"
VARIANT="Container Image"
VARIANT_ID=container
'''
    
    self.assertEqual( 'linux', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').system() )
    self.assertEqual( 'fedora', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').distro() )
    self.assertEqual( 'redhat', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').family() )
    self.assertEqual( '29', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').version_major() )
    self.assertEqual( None, LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').version_minor() )
    self.assertEqual( 'x86_64', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').arch() )

  def test_linux_os_release_alpine_310(self):
    PLAT = self.fake_linux_platform

    OS_RELEASE = '''\
NAME="Alpine Linux"
ID=alpine
VERSION_ID=3.10.4
PRETTY_NAME="Alpine Linux v3.10"
HOME_URL="https://alpinelinux.org/"
BUG_REPORT_URL="https://bugs.alpinelinux.org/"
'''
    
    self.assertEqual( 'linux', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').system() )
    self.assertEqual( 'alpine', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').distro() )
    self.assertEqual( 'alpine', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').family() )
    self.assertEqual( '3', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').version_major() )
    self.assertEqual( '10', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').version_minor() )
    self.assertEqual( 'x86_64', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').arch() )

  def test_linux_os_release_ubuntu_14(self):
    PLAT = self.fake_linux_platform

    OS_RELEASE = '''\
NAME="Ubuntu"
VERSION="14.04.6 LTS, Trusty Tahr"
ID=ubuntu
ID_LIKE=debian
PRETTY_NAME="Ubuntu 14.04.6 LTS"
VERSION_ID="14.04"
HOME_URL="http://www.ubuntu.com/"
SUPPORT_URL="http://help.ubuntu.com/"
BUG_REPORT_URL="http://bugs.launchpad.net/ubuntu/"
'''
    
    self.assertEqual( 'linux', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').system() )
    self.assertEqual( 'ubuntu', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').distro() )
    self.assertEqual( 'debian', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').family() )
    self.assertEqual( '14', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').version_major() )
    self.assertEqual( '04', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').version_minor() )
    self.assertEqual( 'x86_64', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').arch() )
    
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
    
  def test_linux_os_release_ubuntu_18(self):
    PLAT = self.fake_linux_platform

    OS_RELEASE = '''\
NAME="Ubuntu"
VERSION="18.04.4 LTS (Bionic Beaver)"
ID=ubuntu
ID_LIKE=debian
PRETTY_NAME="Ubuntu 18.04.4 LTS"
VERSION_ID="18.04"
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
VERSION_CODENAME=bionic
UBUNTU_CODENAME=bionic
'''
    
    self.assertEqual( 'linux', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').system() )
    self.assertEqual( 'ubuntu', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').distro() )
    self.assertEqual( 'debian', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').family() )
    self.assertEqual( '18', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').version_major() )
    self.assertEqual( '04', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').version_minor() )
    self.assertEqual( 'x86_64', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').arch() )

  def test_linux_os_release_ubuntu_20(self):
    PLAT = self.fake_linux_platform

    OS_RELEASE = '''\
NAME="Ubuntu"
VERSION="20.04 LTS (Focal Fossa)"
ID=ubuntu
ID_LIKE=debian
PRETTY_NAME="Ubuntu Focal Fossa (development branch)"
VERSION_ID="20.04"
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
VERSION_CODENAME=focal
UBUNTU_CODENAME=focal
'''
    
    self.assertEqual( 'linux', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').system() )
    self.assertEqual( 'ubuntu', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').distro() )
    self.assertEqual( 'debian', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').family() )
    self.assertEqual( '20', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').version_major() )
    self.assertEqual( '04', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').version_minor() )
    self.assertEqual( 'x86_64', LINUX_OS_REL(PLAT('x86_64'), OS_RELEASE, '<unittest>').arch() )

if __name__ == '__main__':
  unittest.main()
