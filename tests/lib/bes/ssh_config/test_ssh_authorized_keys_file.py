#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.fs.file_util import file_util
from bes.key_value.key_value_list import key_value_list

from bes.testing.unit_test import unit_test

from bes.ssh_config.ssh_authorized_keys_file import ssh_authorized_keys_file
from bes.ssh_config.ssh_authorized_key import ssh_authorized_key
from bes.ssh_config.ssh_config_error import ssh_config_error

class test_ssh_authorized_keys_file(unit_test):

  def test_basic(self):
    content = '''
ssh-rsa key1 fred@bedrock
ssh-rsa key2 wilman@bedrock
ssh-rsa key3 barney@bedrock
'''
    tmp_file = self.make_temp_file(content = content)
    c = ssh_authorized_keys_file(tmp_file)

    self.assertMultiLineEqual( content.strip(), str(c).strip() )

  def test_add_authorized_key(self):
    content = '''
ssh-rsa key1 fred@bedrock
ssh-rsa key2 wilman@bedrock
ssh-rsa key3 barney@bedrock
'''
    tmp_file = self.make_temp_file(content = content)
    c = ssh_authorized_keys_file(tmp_file)
    c.add_authorized_key(ssh_authorized_key('ssh-rsa', 'key4', 'bambam@bedrock'))

    expected = '''
ssh-rsa key1 fred@bedrock
ssh-rsa key2 wilman@bedrock
ssh-rsa key3 barney@bedrock
ssh-rsa key4 bambam@bedrock
'''
    
    self.assertMultiLineEqual( expected.strip(), file_util.read(tmp_file, codec = 'utf-8').strip() )

  def test_empty_file(self):
    content = '''
'''
    tmp_file = self.make_temp_file(content = content)
    c = ssh_authorized_keys_file(tmp_file)
    c.add_authorized_key(ssh_authorized_key('ssh-rsa', 'key4', 'bambam@bedrock'))

    expected = '''
ssh-rsa key4 bambam@bedrock
'''
    self.assertMultiLineEqual( expected.strip(), file_util.read(tmp_file, codec = 'utf-8').strip() )

  def test_nonexistent_file(self):
    tmp_file = self.make_temp_file()
    file_util.remove(tmp_file)
    c = ssh_authorized_keys_file(tmp_file)
    c.add_authorized_key(ssh_authorized_key('ssh-rsa', 'key4', 'bambam@bedrock'))

    expected = '''
ssh-rsa key4 bambam@bedrock
'''
    self.assertMultiLineEqual( expected.strip(), file_util.read(tmp_file, codec = 'utf-8').strip() )

  def test_comment_preservation(self):
    content = '''
# fred
ssh-rsa key1 fred@bedrock
# wilma
ssh-rsa key2 wilman@bedrock
# barney
ssh-rsa key3 barney@bedrock
'''
    tmp_file = self.make_temp_file(content = content)
    c = ssh_authorized_keys_file(tmp_file)

    self.assertMultiLineEqual( content.strip(), str(c).strip() )
    
if __name__ == '__main__':
  unit_test.main()
