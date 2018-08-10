#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.system.platform_db import _platform_determiner_macos
from bes.system.platform_db import _platform_determiner_linux

class test_platform_db(unittest.TestCase):

  class fake_macos_platform(object):

    def __init__(self, version, arch):
      self._version = version
      self._arch = arch

    def mac_ver(self):
      return ( self._version, ('', '', ''), self._arch )
      
    def machine(self):
      return self._arch
  
  def test__platform_determiner_macos(self):
    D = _platform_determiner_macos
    P = self.fake_macos_platform

    self.assertEqual( 'macos', D(P('10.13', 'x86_64')).system() )
    self.assertEqual( 'macos', D(P('10.13.5', 'x86_64')).system() )

    self.assertEqual( 'yosemite', D(P('10.10.1', 'x86_64')).codename() )
    self.assertEqual( 'el_capitan', D(P('10.11.1', 'x86_64')).codename() )
    self.assertEqual( 'sierra', D(P('10.12.1', 'x86_64')).codename() )
    self.assertEqual( 'high_sierra', D(P('10.13.5', 'x86_64')).codename() )

    self.assertEqual( 'x86_64', D(P('10.13', 'x86_64')).arch() )

    self.assertEqual( None, D(P('10.13', 'x86_64')).distro() )
    self.assertEqual( None, D(P('10.13', 'x86_64')).family() )

    UBUNTU_16_04_issue = '''
Ubuntu 16.04.5 LTS \n \l
'''

    RASPBIAN_9_issue = '''
Raspbian GNU/Linux 9 \n \l
'''

  UBUNTU_16_04_LSB_RELEASE = '''Distributor ID:	Ubuntu
Description:	Ubuntu 16.04.5 LTS
Release:	16.04
Codename:	xenial
'''

  class fake_linux_platform(object):

    def __init__(self, arch):
      self._arch = arch

    def machine(self):
      return self._arch
    
  def test__platform_determiner_linux(self):
    D = _platform_determiner_linux
    P = self.fake_linux_platform

    self.assertEqual( 'linux', D(P('x86_64'), self.UBUNTU_16_04_LSB_RELEASE).system() )
    self.assertEqual( 'xenial', D(P('x86_64'), self.UBUNTU_16_04_LSB_RELEASE).codename() )
    self.assertEqual( 'debian', D(P('x86_64'), self.UBUNTU_16_04_LSB_RELEASE).family() )
    self.assertEqual( '16.04', D(P('x86_64'), self.UBUNTU_16_04_LSB_RELEASE).version() )
    
if __name__ == '__main__':
  unittest.main()
