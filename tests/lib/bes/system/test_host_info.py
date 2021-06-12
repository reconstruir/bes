#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.system.host_info import host_info

class test_host_info(unit_test):

  def test_parse(self):
    self.assertEqual( host_info('windows', '10', '0', 'x86_64', '', None, None), host_info.parse('windows-10-x86_64') )
    self.assertEqual( host_info('windows', '10', '0', 'x86_64', '', None, None), host_info.parse('windows-10') )
    self.assertEqual( host_info('macos', '10', '15', 'x86_64', '', None, None), host_info.parse('macos-10.15-x86_64') )
    self.assertEqual( host_info('macos', '10', '0', 'x86_64', '', None, None), host_info.parse('macos-10-x86_64') )
    self.assertEqual( host_info('macos', '10', '15', 'x86_64', '', None, None), host_info.parse('macos-10.15') )

if __name__ == '__main__':
  unit_test.main()
