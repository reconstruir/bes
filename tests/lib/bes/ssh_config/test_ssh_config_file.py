#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.fs.file_util import file_util
from bes.key_value.key_value_list import key_value_list

from bes.testing.unit_test import unit_test

from bes.ssh_config.ssh_config_file import ssh_config_file

class test_ssh_config_file(unit_test):

  def test___str__(self):
    content = '''
Host kiwi
  User fred
  IdentityFile ~/.ssh/id_rsa
  IdentitiesOnly yes

Host lemon
  User fred
  IdentityFile ~/.ssh/id_rsa

Host lemon
  User fred
  IdentityFile ~/.ssh/id_rsa
  Hostname 172.16.1.1
  Port 666

Host *
  IPQoS=throughput
'''
    tmp_file = self.make_temp_file(content = content)
    c = ssh_config_file(tmp_file)
    self.assert_string_equal( content, str(c), strip = True, multi_line = True, native_line_breaks = True )
    
  def test_update_host_new_hostname(self):
    content = '''
Host kiwi
  User fred
  IdentityFile ~/.ssh/id_rsa
  IdentitiesOnly yes

Host lemon
  User fred
  IdentityFile ~/.ssh/id_rsa

Host apple
  User fred
  IdentityFile ~/.ssh/id_rsa
  Hostname 172.16.1.1
  Port 666

Host *
  IPQoS=throughput
'''
    tmp_file = self.make_temp_file(content = content)
    c = ssh_config_file(tmp_file)
    c.update_host('orange', key_value_list.parse('User=sally IdentityFile=~/.ssh/sally_id_rsa'))

    expected = '''
Host kiwi
  User fred
  IdentityFile ~/.ssh/id_rsa
  IdentitiesOnly yes

Host lemon
  User fred
  IdentityFile ~/.ssh/id_rsa

Host apple
  User fred
  IdentityFile ~/.ssh/id_rsa
  Hostname 172.16.1.1
  Port 666

Host *
  IPQoS=throughput

Host orange
  User sally
  IdentityFile ~/.ssh/sally_id_rsa
'''
    
    self.assert_text_file_equal( expected, tmp_file, codec = 'utf-8', strip = True, native_line_breaks = True )
    
  def test_update_host_dict_values(self):
    content = '''
Host kiwi
  User fred
  IdentityFile ~/.ssh/id_rsa
  IdentitiesOnly yes

Host lemon
  User fred
  IdentityFile ~/.ssh/id_rsa

Host apple
  User fred
  IdentityFile ~/.ssh/id_rsa
  Hostname 172.16.1.1
  Port 666

Host *
  IPQoS=throughput
'''
    tmp_file = self.make_temp_file(content = content)
    c = ssh_config_file(tmp_file)
    c.update_host('orange', { 'User': 'sally', 'IdentityFile': '~/.ssh/sally_id_rsa', 'Port': '666' })

    expected = '''
Host kiwi
  User fred
  IdentityFile ~/.ssh/id_rsa
  IdentitiesOnly yes

Host lemon
  User fred
  IdentityFile ~/.ssh/id_rsa

Host apple
  User fred
  IdentityFile ~/.ssh/id_rsa
  Hostname 172.16.1.1
  Port 666

Host *
  IPQoS=throughput

Host orange
  IdentityFile ~/.ssh/sally_id_rsa
  Port 666
  User sally
'''
    
    self.assert_text_file_equal( expected, tmp_file, codec = 'utf-8', strip = True, native_line_breaks = True )

  def test_update_host_string_values(self):
    content = '''
Host kiwi
  User fred
  IdentityFile ~/.ssh/id_rsa
  IdentitiesOnly yes

Host lemon
  User fred
  IdentityFile ~/.ssh/id_rsa

Host apple
  User fred
  IdentityFile ~/.ssh/id_rsa
  Hostname 172.16.1.1
  Port 666

Host *
  IPQoS=throughput
'''
    tmp_file = self.make_temp_file(content = content)
    c = ssh_config_file(tmp_file)
    c.update_host('orange', 'User=sally IdentityFile=~/.ssh/sally_id_rsa Port=666')

    expected = '''
Host kiwi
  User fred
  IdentityFile ~/.ssh/id_rsa
  IdentitiesOnly yes

Host lemon
  User fred
  IdentityFile ~/.ssh/id_rsa

Host apple
  User fred
  IdentityFile ~/.ssh/id_rsa
  Hostname 172.16.1.1
  Port 666

Host *
  IPQoS=throughput

Host orange
  User sally
  IdentityFile ~/.ssh/sally_id_rsa
  Port 666
'''
    
  def test_empty_file(self):
    content = '''
'''
    tmp_file = self.make_temp_file(content = content)
    c = ssh_config_file(tmp_file)

    self.assert_string_equal( content, str(c), strip = True, multi_line = True, native_line_breaks = True )
    
  def test_non_existent_file(self):
    tmp_file = self.make_temp_file()
    file_util.remove(tmp_file)
    c = ssh_config_file(tmp_file)

    self.assert_string_equal( '', str(c), strip = True, multi_line = True, native_line_breaks = True )
    c.update_host('orange', key_value_list.parse('User=sally IdentityFile=~/.ssh/sally_id_rsa'))

    expected = '''
Host orange
  User sally
  IdentityFile ~/.ssh/sally_id_rsa
'''
    self.assert_text_file_equal( expected, tmp_file, codec = 'utf-8', strip = True, native_line_breaks = True )
    
  def test_find_host(self):
    content = '''
Host kiwi
  User fred
  IdentityFile ~/.ssh/id_fred_rsa
  IdentitiesOnly yes

Host lemon
  User sally
  IdentityFile ~/.ssh/id_sally_rsa

Host lemon
  User fred
  IdentityFile ~/.ssh/id_memon_rsa
  Hostname 172.16.1.1
  Port 666

Host *
  IPQoS=throughput
'''
    tmp_file = self.make_temp_file(content = content)
    c = ssh_config_file(tmp_file)
    s = c.find_host('lemon')
    self.assertEqual( 'sally', s.User )
    self.assertEqual( '~/.ssh/id_sally_rsa', s.IdentityFile )

  def test_update_host_existing_hostname(self):
    content = '''
Host kiwi
  User fred
  IdentityFile ~/.ssh/id_rsa
  IdentitiesOnly yes

Host lemon
  User fred
  IdentityFile ~/.ssh/id_rsa

Host apple
  User fred
  IdentityFile ~/.ssh/id_rsa
  Hostname 172.16.1.1
  Port 666

Host *
  IPQoS=throughput
'''
    tmp_file = self.make_temp_file(content = content)
    c = ssh_config_file(tmp_file)
    c.update_host('apple', key_value_list.parse('User=sally IdentityFile=~/.ssh/sally_id_rsa'))

    expected = '''
Host kiwi
  User fred
  IdentityFile ~/.ssh/id_rsa
  IdentitiesOnly yes

Host lemon
  User fred
  IdentityFile ~/.ssh/id_rsa

Host apple
  User sally
  IdentityFile ~/.ssh/sally_id_rsa

Host *
  IPQoS=throughput
'''
    
    self.assert_text_file_equal( expected, tmp_file, codec = 'utf-8', strip = True, native_line_breaks = True )
    
if __name__ == '__main__':
  unit_test.main()
