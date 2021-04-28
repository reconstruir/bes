#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.pyinstaller.pyinstaller import pyinstaller
from bes.ssh_config.ssh_config_manager import ssh_config_manager
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_skip_class import unit_test_skip_class

class test_ssh_config_manager(unit_test):

  @classmethod
  def setUpClass(clazz):
    unit_test_skip_class.raise_skip_if_not_unix()
    pyinstaller.raise_skip_if_is_binary()

  def test_nothing(self):
    tmp_dir = self.make_temp_dir(suffix = '.ssh')
    cm = ssh_config_manager(tmp_dir)
    self.assertEqual( [], file_find.find(tmp_dir, relative = True) )
    
  def test_add_config_host_clean_slate(self):
    tmp_dir = self.make_temp_dir(suffix = '.ssh')
    cm = ssh_config_manager(tmp_dir)
    cm.add_config_host('foo', 'Hostname=192.168.1.2 IdentityFile=/tmp/id_rsa User=fred')
    files = file_find.find(tmp_dir, relative = True)
    self.assertEqual( [
      'config',
    ], files )

    expected_config = '''
Host foo
  Hostname 192.168.1.2
  IdentityFile /tmp/id_rsa
  User fred
'''
    self.assertMultiLineEqual( expected_config.strip(), file_util.read(path.join(tmp_dir, 'config'), codec = 'utf-8').strip() )

  def test_add_known_host_clean_slate(self):
    tmp_dir = self.make_temp_dir(suffix = '.ssh')
    cm = ssh_config_manager(tmp_dir)
    cm.add_known_host([ 'example.com' ], 'ssh-rsa', 'key1')
    files = file_find.find(tmp_dir, relative = True)
    self.assertEqual( [
      'known_hosts',
    ], files )

    expected_known_hosts = '''
example.com ssh-rsa key1
'''
    self.assertMultiLineEqual( expected_known_hosts.strip(), file_util.read(path.join(tmp_dir, 'known_hosts'), codec = 'utf-8').strip() )

  def test_add_authorized_key_clean_slate(self):
    tmp_dir = self.make_temp_dir(suffix = '.ssh')
    cm = ssh_config_manager(tmp_dir)
    cm.add_authorized_key('ssh-rsa', 'key1', 'fred@bedrock')
    files = file_find.find(tmp_dir, relative = True)
    self.assertEqual( [
      'authorized_keys',
    ], files )

    expected_authorized_keys = '''
ssh-rsa key1 fred@bedrock
'''
    self.assertMultiLineEqual( expected_authorized_keys.strip(), file_util.read(path.join(tmp_dir, 'authorized_keys'), codec = 'utf-8').strip() )
    
  def test_install_key_pair_for_host(self):
    tmp_dir = self.make_temp_dir(suffix = '.ssh')
    cm = ssh_config_manager(tmp_dir)
    tmp_public_key = 'publickey'
    tmp_private_key = 'privatekey'
    tmp_hostname = 'bitbucket.org'

    installed = cm.install_key_pair_for_host('publickey',
                                             'privatekey',
                                             'bitbucket.org',
                                             username = 'fred',
                                             include_ip_address = False,
                                             include_comment = False)

    files = file_find.find(tmp_dir, relative = True)
    self.assertEqual( [
      'config',
      'id_rsa_bitbucket_org',
      'id_rsa_bitbucket_org.pub',
      'known_hosts',
    ], files )

    expected_config = '''
Host bitbucket.org
  Hostname bitbucket.org
  IdentityFile {private_key}
  User fred
'''.format(private_key = installed.private_key_filename)
    self.assertMultiLineEqual( expected_config.strip(), file_util.read(path.join(tmp_dir, 'config'), codec = 'utf-8').strip() )

    expected_known_hosts = '''
bitbucket.org ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAubiN81eDcafrgMeLzaFPsw2kNvEcqTKl/VqLat/MaB33pZy0y3rJZtnqwR2qOOvbwKZYKiEO1O6VqNEBxKvJJelCq0dTXWT5pbO2gDXC6h6QDXCaHo6pOHGPUy+YBaGQRGuSusMEASYiWunYN0vCAI8QaXnWMXNMdFP3jHAJH0eDsoiGnLPBlBp4TNm6rYI74nMzgz3B9IikW4WVK+dc8KZJZWYjAuORU3jc1c/NPskD2ASinf8v3xnfXeukU0sJ5N6m5E8VLjObPEO+mN2t/FZTMZLiFqPWc/ALSqnMnnhwrNi2rbfg/rd/IpL8Le3pSBne8+seeFVBoGqzHM9yXw==
'''
    self.assertMultiLineEqual( expected_known_hosts.strip(), file_util.read(path.join(tmp_dir, 'known_hosts'), codec = 'utf-8').strip() )

    abs_files = [ path.join(tmp_dir, f) for f in files ]
    for filename in abs_files:
      self.assertEqual( 0o0600, file_util.mode(filename) )
    
if __name__ == '__main__':
  unit_test.main()
