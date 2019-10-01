#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
print('HERE1')
import unittest
print('HERE2')

class test_bes_test(unittest.TestCase):
  print('HERE3')

  def test_foo(self):
    print('HERE4')
    self.assertEqual( 666, 665 + 1 )
    print('HERE5')

if __name__ == '__main__':
  print('HERE6')
  unittest.main()
