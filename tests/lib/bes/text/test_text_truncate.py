#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.text.text_truncate import text_truncate

class test_text_truncate(unittest.TestCase):

  def test_truncate(self):
    self.assertEqual( 'kiw..ple',
                      text_truncate.truncate('kiwi and apple', 8) )
    self.assertEqual( 'kiwi..ple',
                      text_truncate.truncate('kiwi and apple', 9) )
    self.assertEqual( 'kiw..nge',
                      text_truncate.truncate('kiwi and orange', 8) )
    self.assertEqual( 'kiwi..nge',
                      text_truncate.truncate('kiwi and orange', 9) )
  
  
if __name__ == '__main__':
  unittest.main()
