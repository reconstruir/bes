#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.system.host import host
from bes.system.host_info import host_info
from bes.system.host_override import host_override
from bes.system.host_override import host_override_func

class test_host_override(unit_test):

  def test_basic(self):
    info = host_info('foo', '666', '42', 'x86_64', 'woof', 'deviant')
    with host_override(info) as over:
      self.assertEqual( 'foo', host.SYSTEM )
      self.assertEqual( '666', host.VERSION_MAJOR )
      self.assertEqual( '42', host.VERSION_MINOR )
      self.assertEqual( 'woof', host.DISTRO )
      self.assertEqual( 'deviant', host.FAMILY )

  @host_override_func(host_info('bar', '123', '43', 'i386', 'meow', 'frubunto'))
  def test_decorator(self):
    self.assertEqual( 'bar', host.SYSTEM )
    self.assertEqual( '123', host.VERSION_MAJOR )
    self.assertEqual( '43', host.VERSION_MINOR )
    self.assertEqual( 'meow', host.DISTRO )
    self.assertEqual( 'frubunto', host.FAMILY )

if __name__ == "__main__":
  unit_test.main()
