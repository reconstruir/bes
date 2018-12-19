#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_attributes as FA, file_util, temp_file
  
class test_file_attributes(unit_test):

  def test_get_never_set(self):
    tmp = temp_file.make_temp_file(content = 'this is foo\n')
    self.assertEqual( None, FA.get(tmp, 'foo') )
  
  def test_set_get(self):
    tmp = temp_file.make_temp_file(content = 'this is foo\n', delete = False)
    FA.set(tmp, 'foo', 'hi')
    self.assertEqual( 'hi', FA.get(tmp, 'foo'))

  def test_empty_keys(self):
    tmp = temp_file.make_temp_file(content = 'this is foo\n', delete = False)
    self.assertEqual( [], FA.keys(tmp) )

  def test_keys(self):
    tmp = temp_file.make_temp_file(content = 'this is foo\n', delete = False)
    FA.set(tmp, 'foo', 'hi')
    FA.set(tmp, 'bar', '99')
    self.assertEqual( [ 'bar', 'foo' ], FA.keys(tmp) )
    
  def test_clear(self):
    tmp = temp_file.make_temp_file(content = 'this is foo\n', delete = False)
    FA.set(tmp, 'foo', 'hi')
    FA.set(tmp, 'bar', '99')
    self.assertEqual( [ 'bar', 'foo' ], FA.keys(tmp) )
    FA.clear(tmp)
    self.assertEqual( [], FA.keys(tmp) )
    
if __name__ == '__main__':
  unit_test.main()
    
