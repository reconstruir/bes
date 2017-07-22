#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.net.util import Network

class test_Network(unittest.TestCase):

  def test_parse_host_port(self):
    self.assertEqual( ( 'foo', 23 ), Network.parse_host_port('foo:23' ) )
    self.assertEqual( ( 'foo', 0 ), Network.parse_host_port('foo:caca' ) )
    self.assertEqual( ( 'foo', 0 ), Network.parse_host_port('foo' ) )
    self.assertEqual( ( 'localhost', 23 ), Network.parse_host_port(':23' ) )
    self.assertEqual( ( 'foo', 23 ), Network.parse_host_port('foo:caca', default_port = 23 ) )
    self.assertEqual( ( 'localhost', 9000 ), Network.parse_host_port(':9000') )

if __name__ == "__main__":
  unittest.main()
