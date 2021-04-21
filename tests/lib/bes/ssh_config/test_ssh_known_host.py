#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.ssh_config.ssh_known_host import ssh_known_host

class test_ssh_known_host(unit_test):

  def test___str__(self):
    self.assertEqual( 'example.com,192.168.2.2 ssh-rsa key4', str(ssh_known_host([ 'example.com', '192.168.2.2' ], 'ssh-rsa', 'key4')) )

  def test___str___with_comment(self):
    self.assertEqual( 'example.com,192.168.2.2 ssh-rsa key4 # foo', str(ssh_known_host([ 'example.com', '192.168.2.2' ], 'ssh-rsa', 'key4', 'foo')) )

  def test_parse_text(self):
    self.assertEqual( ssh_known_host([ 'example.com', '192.168.2.2' ], 'ssh-rsa', 'key4'),
                      ssh_known_host.parse_text('example.com,192.168.2.2 ssh-rsa key4') )

  def test_parse_text_with_comment(self):
    self.assertEqual( ssh_known_host([ 'example.com', '192.168.2.2' ], 'ssh-rsa', 'key4', 'foo'),
                      ssh_known_host.parse_text('example.com,192.168.2.2 ssh-rsa key4 # foo') )
    
  def test_parse_text_with_comment_and_spaces(self):
    self.assertEqual( ssh_known_host([ 'example.com' ], 'ssh-rsa', 'key4', 'foo  bar   baz'),
                      ssh_known_host.parse_text('example.com ssh-rsa key4 # foo  bar   baz') )

if __name__ == '__main__':
  unit_test.main()
