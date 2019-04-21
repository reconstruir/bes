#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.property.cached_property import cached_property

class test_cached_property(unittest.TestCase):

  def test_simple(self):
    class foo(object):

      def __init__(self):
        self._count = 0
      
      @cached_property
      def value(self):
        self._count += 1
        return 666

    f = foo()
    self.assertEqual( 0, f._count )
    self.assertEqual( 666, f.value )
    self.assertEqual( 1, f._count )
    self.assertEqual( 666, f.value )
    self.assertEqual( 1, f._count )

if __name__ == '__main__':
  unittest.main()
