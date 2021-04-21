#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.fs.file_util import file_util
from bes.pyinstaller.pyinstaller import pyinstaller
from bes.ssh_config.ssh_key_scan import ssh_key_scan
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_skip_class import unit_test_skip_class

class test_ssh_key_scan(unit_test):

  @classmethod
  def setUpClass(clazz):
    unit_test_skip_class.raise_skip_if_not_unix()
    pyinstaller.raise_skip_if_is_binary()

  def test_scan(self):
    s = ssh_key_scan.scan('bitbucket.org')
    self.assertEqual( 2, len(s.hostnames) )
    self.assertEqual( 'bitbucket.org', s.hostnames[0] )
    self.assertEqual( 'ssh-rsa', s.key_type )
    self.assertEqual( 'AAAAB3NzaC1yc2EAAAABIwAAAQEAubiN81eDcafrgMeLzaFPsw2kNvEcqTKl/VqLat/MaB33pZy0y3rJZtnqwR2qOOvbwKZYKiEO1O6VqNEBxKvJJelCq0dTXWT5pbO2gDXC6h6QDXCaHo6pOHGPUy+YBaGQRGuSusMEASYiWunYN0vCAI8QaXnWMXNMdFP3jHAJH0eDsoiGnLPBlBp4TNm6rYI74nMzgz3B9IikW4WVK+dc8KZJZWYjAuORU3jc1c/NPskD2ASinf8v3xnfXeukU0sJ5N6m5E8VLjObPEO+mN2t/FZTMZLiFqPWc/ALSqnMnnhwrNi2rbfg/rd/IpL8Le3pSBne8+seeFVBoGqzHM9yXw==', s.key )
    self.assertTrue( s.comment.startswith('# bitbucket.org:22 SSH-2.0') )
    
if __name__ == '__main__':
  unit_test.main()
