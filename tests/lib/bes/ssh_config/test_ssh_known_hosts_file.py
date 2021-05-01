#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.fs.file_util import file_util
from bes.key_value.key_value_list import key_value_list

from bes.testing.unit_test import unit_test

from bes.ssh_config.ssh_known_hosts_file import ssh_known_hosts_file
from bes.ssh_config.ssh_known_host import ssh_known_host
from bes.ssh_config.ssh_config_error import ssh_config_error

class test_ssh_known_hosts_file(unit_test):

  def test_basic(self):
    content = '''
example.com.172.16.1.1 ecdsa-sha2-nistp256 key1
bitbucket.org,18.205.93.2 ssh-rsa key2
198.168.1.1 ssh-rsa key3
'''
    tmp_file = self.make_temp_file(content = content)
    c = ssh_known_hosts_file(tmp_file)

    self.assertMultiLineEqual( content.strip(), str(c).strip() )

  def test_add_known_host(self):
    content = '''
example.com.172.16.1.1 ecdsa-sha2-nistp256 key1
bitbucket.org,18.205.93.2 ssh-rsa key2
198.168.1.1 ssh-rsa key3
'''
    tmp_file = self.make_temp_file(content = content)
    c = ssh_known_hosts_file(tmp_file)
    c.add_known_host(ssh_known_host([ 'foo.com', '192.168.2.2' ], 'ssh-rsa', 'key4'))

    expected = '''
example.com.172.16.1.1 ecdsa-sha2-nistp256 key1
bitbucket.org,18.205.93.2 ssh-rsa key2
198.168.1.1 ssh-rsa key3
foo.com,192.168.2.2 ssh-rsa key4
'''
    
    self.assertMultiLineEqual( expected.strip(), file_util.read(tmp_file, codec = 'utf-8').strip() )

  def test_empty_file(self):
    content = '''
'''
    tmp_file = self.make_temp_file(content = content)
    c = ssh_known_hosts_file(tmp_file)
    c.add_known_host(ssh_known_host([ 'foo.com', '192.168.2.2' ], 'ssh-rsa', 'key4'))

    expected = '''
foo.com,192.168.2.2 ssh-rsa key4
'''
    self.assertMultiLineEqual( expected.strip(), file_util.read(tmp_file, codec = 'utf-8').strip() )

  def test_nonexistent_file(self):
    tmp_file = self.make_temp_file()
    file_util.remove(tmp_file)
    c = ssh_known_hosts_file(tmp_file)
    c.add_known_host(ssh_known_host([ 'foo.com', '192.168.2.2' ], 'ssh-rsa', 'key4'))

    expected = '''
foo.com,192.168.2.2 ssh-rsa key4
'''
    
    self.assertMultiLineEqual( expected.strip(), file_util.read(tmp_file, codec = 'utf-8').strip() )

  def test_comment_preservation(self):
    content = '''
# kiwi
example.com.172.16.1.1 ecdsa-sha2-nistp256 key1
# apple
bitbucket.org,18.205.93.2 ssh-rsa key2
# lemon
198.168.1.1 ssh-rsa key3
'''
    tmp_file = self.make_temp_file(content = content)
    c = ssh_known_hosts_file(tmp_file)

    self.assertMultiLineEqual( content.strip(), str(c).strip() )
    
  def test_find_known_host(self):
    content = '''
example.com.172.16.1.1 ecdsa-sha2-nistp256 key1
bitbucket.org,18.205.93.2 ssh-rsa key2
198.168.1.1 ssh-rsa key3
'''
    tmp_file = self.make_temp_file(content = content)
    c = ssh_known_hosts_file(tmp_file)
    self.assertEqual( ( [ 'bitbucket.org', '18.205.93.2' ], 'ssh-rsa', 'key2', None ),
                      c.find_known_host('bitbucket.org') )
    
  def test_malformed_file(self):
    content = '''
example.com.172.16.1.1 ecdsa-sha2-nistp256 key1
wtf
bitbucket.org,18.205.93.2 ssh-rsa key2
198.168.1.1 ssh-rsa key3
'''
    tmp_file = self.make_temp_file(content = content)
    c = ssh_known_hosts_file(tmp_file)
    with self.assertRaises(ssh_config_error) as ctx:
      c.find_known_host('bitbucket.org')
    
if __name__ == '__main__':
  unit_test.main()
