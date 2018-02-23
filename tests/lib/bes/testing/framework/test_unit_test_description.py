#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.testing.framework import unit_test_description as UTD
  
class test_unit_test_description(unit_test):

  def test_parse(self):
    self.assertEqual( ( 'foo.py', 'fix', 'func' ), UTD.parse('foo.py:fix.func') )
    self.assertEqual( ( 'foo.py', None, None ), UTD.parse('foo.py') )
    self.assertEqual( ( 'foo.py', None, None ), UTD.parse('foo.py:') )
    self.assertEqual( ( 'foo.py', None, 'fix' ), UTD.parse('foo.py:fix') )
    
  def test_parse_no_filename(self):
    self.assertEqual( ( None, 'fix', 'func' ), UTD.parse(':fix.func') )
    self.assertEqual( ( None, None, 'fix' ), UTD.parse(':fix') )
    
if __name__ == '__main__':
  unit_test.main()
    
