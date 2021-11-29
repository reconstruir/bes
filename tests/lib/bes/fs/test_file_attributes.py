#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs.file_attributes import file_attributes as FA
from bes.fs.file_util import file_util
from bes.docker.docker import docker
  
class test_file_attributes(unit_test):

  @classmethod
  def setUpClass(clazz):
    docker.raise_skip_if_running_under_docker()
  
  def test_get_never_set(self):
    tmp = self._make_temp_file('this is foo\n')
    self.assertEqual( None, FA.get(tmp, 'foo') )
  
  def test_set_get(self):
    tmp = self._make_temp_file('this is foo\n')
    FA.set(tmp, 'foo', 'hi'.encode('utf-8'))
    self.assertEqual( 'hi', FA.get(tmp, 'foo').decode('utf-8') )

  def test_empty_keys(self):
    tmp = self._make_temp_file('this is foo\n')
    self.assertEqual( [], self._munge_attr_keys(FA.keys(tmp)) )

  def test_keys(self):
    tmp = self._make_temp_file('this is foo\n')
    FA.set(tmp, 'foo', 'hi'.encode('utf-8'))
    FA.set(tmp, 'bar', '99'.encode('utf-8'))
    self.assertEqual( [ 'bar', 'foo' ], self._munge_attr_keys(FA.keys(tmp)) )
    
  def test_clear(self):
    tmp = self._make_temp_file('this is foo\n')
    FA.set(tmp, 'foo', 'hi'.encode('utf-8'))
    FA.set(tmp, 'bar', '99'.encode('utf-8'))
    self.assertEqual( [ 'bar', 'foo' ], self._munge_attr_keys(FA.keys(tmp)) )
    FA.clear(tmp)
    self.assertEqual( [], self._munge_attr_keys(FA.keys(tmp)) )

  @classmethod
  def _munge_attr_keys(clazz, keys):
    'On some linux systems, there is an extra selinux key in many attr results'
    assert isinstance(keys, list)
    return [ key for key in keys if key != 'selinux' ]

  def _make_temp_file(self, content):
    # Use a temporary directory in the same filesystem ad the code to avoid the
    # issue that on some platforms the tmp dir filesystem might have attributes disabled.
    tmp_dir = path.join(path.dirname(__file__), '.tmp')
    return self.make_temp_file(content = content, dir = tmp_dir, suffix = '.txt')
    
if __name__ == '__main__':
  unit_test.main()
    
