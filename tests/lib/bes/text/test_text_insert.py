#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.text.text_insert import text_insert
from bes.testing.unit_test import unit_test

class test_text_insert(unit_test):

  def test_insert(self):
    f = text_insert.insert
    self.assertEqual( 'foothis is source', f('this is source', 0, 'foo') )
    self.assertEqual( 'tfoohis is source', f('this is source', 1, 'foo') )
    self.assertEqual( 'tfhis is source', f('this is source', 1, 'f') )
    self.assertEqual( 'this is source', f('this is source', 1, '') )
    self.assertEqual( 'this', f('this', 0, '') )
    self.assertEqual( 'this', f('this', 1, '') )
    self.assertEqual( 'this', f('this', 2, '') )
    self.assertEqual( 'this', f('this', 3, '') )
    self.assertEqual( 'this', f('this', 4, '') )
    self.assertEqual( '_this', f('this', 0, '_') )
    self.assertEqual( 't_his', f('this', 1, '_') )
    self.assertEqual( 'th_is', f('this', 2, '_') )
    self.assertEqual( 'thi_s', f('this', 3, '_') )
    self.assertEqual( 'this_', f('this', 4, '_') )
    self.assertEqual( 'this_', f('this', 5, '_') )
    
if __name__ == '__main__':
  unit_test.main()
