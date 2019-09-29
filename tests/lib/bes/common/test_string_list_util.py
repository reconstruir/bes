#!/usr/bin/env python3
#-*- coding:utf-8 -*-
#
import unittest
from bes.common.string_list_util import string_list_util

class test_string_list_util(unittest.TestCase):

  def test_remove_if(self):
    f = string_list_util.remove_if
    self.assertEqual( [ 'a', 'b', 'c' ], f( [ 'a', 'b', 'c' ], [] ) )
    self.assertEqual( [], f( [ 'a', 'b', 'c' ], [ 'a', 'b', 'c' ] ) )
    self.assertEqual( [ 'a' ], f( [ 'a', 'b', 'c' ], [ 'b', 'c' ] ) )

  def test_to_string(self):
    f = string_list_util.to_string
    self.assertEqual( 'a;b;c', f([ 'a', 'b', 'c' ]) )
    self.assertEqual( 'a b c', f([ 'a', 'b', 'c' ], delimiter = ' ') )
    self.assertEqual( '"a x" b c', f([ 'a x', 'b', 'c' ], delimiter = ' ', quote = True) )
    
if __name__ == "__main__":
  unittest.main()
