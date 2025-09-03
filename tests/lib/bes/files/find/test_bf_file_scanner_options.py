#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.files.match.bf_file_matcher import bf_file_matcher
from bes.files.find.bf_file_scanner_options import bf_file_scanner_options

from bes.testing.unit_test import unit_test

class test_bf_file_scanner_options(unit_test):

  def test_clone__eq__(self):
    o1 = bf_file_scanner_options()
    o1.stop_after = 2
    o2 = o1.clone()
    self.assertEqual( o1, o2 )

  def test_clone_not__eq__(self):
    o1 = bf_file_scanner_options()
    o2 = o1.clone()
    o1.stop_after = 2
    self.assertNotEqual( o1, o2 )
    
if __name__ == '__main__':
  unit_test.main()
