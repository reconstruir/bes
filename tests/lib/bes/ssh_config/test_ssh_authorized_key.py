#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.ssh_config.ssh_authorized_key import ssh_authorized_key

class test_ssh_authorized_key(unit_test):

  def test___str__(self):
    self.assertEqual( 'ssh-rsa key4 fred@bedrock', str(ssh_authorized_key('ssh-rsa', 'key4', 'fred@bedrock')) )

  def test___str___with_spaces(self):
    self.assertEqual( 'ssh-rsa key4 fred   @   bedrock', str(ssh_authorized_key('ssh-rsa', 'key4', 'fred   @   bedrock')) )
    self.assertEqual( 'ssh-rsa key4 fred   @   bedrock  ', str(ssh_authorized_key('ssh-rsa', 'key4', 'fred   @   bedrock  ')) )

  def test_parse_text(self):
    self.assertEqual( ssh_authorized_key('ssh-rsa', 'key4', 'fred@bedrock'),
                      ssh_authorized_key.parse_text('ssh-rsa key4 fred@bedrock') )

  def test_parse_text_with_spaces(self):
    self.assertEqual( ssh_authorized_key('ssh-rsa', 'key4', 'fred  @  bedrock'),
                      ssh_authorized_key.parse_text('ssh-rsa key4 fred  @  bedrock') )
    self.assertEqual( ssh_authorized_key('ssh-rsa', 'key4', 'fred  @  bedrock'),
                      ssh_authorized_key.parse_text('ssh-rsa key4   fred  @  bedrock  ') )

if __name__ == '__main__':
  unit_test.main()
