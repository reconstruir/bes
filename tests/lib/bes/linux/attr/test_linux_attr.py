#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.linux.attr.linux_attr import linux_attr
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_class_skip import unit_test_class_skip

from _bes_unit_test_common.unit_test_media import unit_test_media

class test_linux_attr(unit_test):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip_if_not_linux()
  
  def test_has_key(self):
    tmp = self.make_temp_file()
    self.assertFalse( linux_attr.has_key(tmp, 'foo') )
    linux_attr.set_string(tmp, 'foo', 'hi')
    self.assertTrue( linux_attr.has_key(tmp, 'foo') )
  
  def test_keys(self):
    tmp = self.make_temp_file()
    self.assertEqual( [], linux_attr.keys(tmp) )
    linux_attr.set_string(tmp, 'foo', 'hi')
    self.assertEqual( [ 'foo' ], linux_attr.keys(tmp) )
    linux_attr.set_string(tmp, 'bar', '666')
    self.assertEqual( [ 'bar', 'foo' ], linux_attr.keys(tmp) )

  def test_set_string_get_string(self):
    tmp = self.make_temp_file()
    linux_attr.set_string(tmp, 'foo', 'hi')
    self.assertEqual( 'hi', linux_attr.get_string(tmp, 'foo') )

  def test_set_string_get_bytes(self):
    tmp = self.make_temp_file()
    linux_attr.set_string(tmp, 'foo', 'hi')
    self.assertEqual( 'hi'.encode('utf-8'), linux_attr.get_bytes(tmp, 'foo') )
    
  def test_set_bytes_get_string(self):
    tmp = self.make_temp_file()
    linux_attr.set_bytes(tmp, 'foo', 'hi'.encode('utf-8'))
    self.assertEqual( 'hi', linux_attr.get_string(tmp, 'foo') )
    
  def test_set_bytes_get_bytes(self):
    tmp = self.make_temp_file()
    data = 'hi'.encode('utf-8')
    linux_attr.set_bytes(tmp, 'foo', data)
    self.assertEqual( data, linux_attr.get_bytes(tmp, 'foo') )

  def test_remove(self):
    tmp = self.make_temp_file()
    self.assertEqual( [], linux_attr.keys(tmp) )
    linux_attr.set_string(tmp, 'foo', 'hi')
    self.assertEqual( [ 'foo' ], linux_attr.keys(tmp) )
    linux_attr.remove(tmp, 'foo')
    self.assertEqual( [], linux_attr.keys(tmp) )

  def test_clear(self):
    tmp = self.make_temp_file()
    self.assertEqual( [], linux_attr.keys(tmp) )
    linux_attr.set_string(tmp, 'foo', 'hi')
    linux_attr.set_string(tmp, 'bar', '666')
    self.assertEqual( [ 'bar', 'foo' ], linux_attr.keys(tmp) )
    linux_attr.clear(tmp)
    self.assertEqual( [], linux_attr.keys(tmp) )

  def test_set_png_get_png(self):
    tmp = self.make_temp_file()
    linux_attr.set_bytes(tmp, 'picture', unit_test_media.PNG_SMALLEST_POSSIBLE)
    self.assertEqual( unit_test_media.PNG_SMALLEST_POSSIBLE, linux_attr.get_bytes(tmp, 'picture') )
    
if __name__ == '__main__':
  unit_test.main()
