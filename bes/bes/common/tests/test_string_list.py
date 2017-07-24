#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.common import string_list

class test_string_list(unittest.TestCase):

  def test_remove_if(self):
    f = string_list.remove_if
    self.assertEqual( [ 'a', 'b', 'c' ], f( [ 'a', 'b', 'c' ], [] ) )
    self.assertEqual( [], f( [ 'a', 'b', 'c' ], [ 'a', 'b', 'c' ] ) )
    self.assertEqual( [ 'a' ], f( [ 'a', 'b', 'c' ], [ 'b', 'c' ] ) )

if __name__ == "__main__":
  unittest.main()
