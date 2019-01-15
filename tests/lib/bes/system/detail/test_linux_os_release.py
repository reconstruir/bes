#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest

from bes.system.detail.linux_os_release import linux_os_release as P

class test_linux_os_release(unittest.TestCase):

  def test_ubuntu(self):
    text = '''\NAME="Ubuntu"
VERSION="18.04.1 LTS (Bionic Beaver)"
ID=ubuntu
ID_LIKE=debian
PRETTY_NAME="Ubuntu 18.04.1 LTS"
VERSION_ID="18.04"
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
VERSION_CODENAME=bionic
UBUNTU_CODENAME=bionic
'''

    self.assertEqual( ( 'ubuntu', '18', '04', 'debian' ), P.parse_os_release(text, '<unittest>') )
    
  def test_alpine(self):
    text = '''\NAME="Alpine Linux"
ID=alpine
VERSION_ID=3.8.2
PRETTY_NAME="Alpine Linux v3.8"
HOME_URL="http://alpinelinux.org"
BUG_REPORT_URL="http://bugs.alpinelinux.org"'''

    self.assertEqual( ( 'alpine', '3', '8', 'alpine' ), P.parse_os_release(text, '<unittest>') )

  def test_raspbian(self):
    text = '''\PRETTY_NAME="Raspbian GNU/Linux 8 (jessie)"
NAME="Raspbian GNU/Linux"
VERSION_ID="8"
VERSION="8 (jessie)"
ID=raspbian
ID_LIKE=debian
HOME_URL="http://www.raspbian.org/"
SUPPORT_URL="http://www.raspbian.org/RaspbianForums"
BUG_REPORT_URL="http://www.raspbian.org/RaspbianBugs"
'''
    self.assertEqual( ( 'raspbian', '8', None, 'debian' ), P.parse_os_release(text, '<unittest>') )
    
if __name__ == '__main__':
  unittest.main()
