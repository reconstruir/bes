#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_attributes as FA, file_util, temp_file
  
class test_file_attributes(unit_test):

  def test_get_never_set(self):
    tmp = self._make_temp_file('this is foo\n')
    self.assertEqual( None, FA.get(tmp, 'foo') )
  
  def test_set_get(self):
    tmp = self._make_temp_file('this is foo\n')
    FA.set(tmp, 'foo', 'hi')
    self.assertEqual( 'hi', FA.get(tmp, 'foo'))

  def test_empty_keys(self):
    tmp = self._make_temp_file('this is foo\n')
    self.assertEqual( [], self._munge_attr_keys(FA.keys(tmp)) )

  def test_keys(self):
    tmp = self._make_temp_file('this is foo\n')
    FA.set(tmp, 'foo', 'hi')
    FA.set(tmp, 'bar', '99')
    self.assertEqual( [ 'bar', 'foo' ], self._munge_attr_keys(FA.keys(tmp)) )
    
  def test_clear(self):
    tmp = self._make_temp_file('this is foo\n')
    FA.set(tmp, 'foo', 'hi')
    FA.set(tmp, 'bar', '99')
    self.assertEqual( [ 'bar', 'foo' ], self._munge_attr_keys(FA.keys(tmp)) )
    FA.clear(tmp)
    self.assertEqual( [], FA.keys(tmp) )

  @classmethod
  def _munge_attr_keys(clazz, keys):
    'On some linux systems, there is an extra selinux key in many attr results'
    assert isinstance(keys, list)
    return [ key for key in keys if key != 'selinux' ]

  def _make_temp_file(self, content):
    tmp_dir = path.join(path.dirname(__file__), '.tmp')
    return temp_file.make_temp_file(content = content, dir = tmp_dir, delete = not self.DEBUG)
    
if __name__ == '__main__':
  unit_test.main()
    
