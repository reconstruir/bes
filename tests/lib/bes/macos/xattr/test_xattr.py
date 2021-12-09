#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.macos.xattr.xattr import xattr

class test_xattr(unit_test):

  def test_has_key(self):
    tmp = self.make_temp_file()
    self.assertFalse( xattr.has_key(tmp, 'foo') )
    xattr.set_string(tmp, 'foo', 'hi')
    self.assertTrue( xattr.has_key(tmp, 'foo') )
  
  def test_keys(self):
    tmp = self.make_temp_file()
    self.assertEqual( [], xattr.keys(tmp) )
    xattr.set_string(tmp, 'foo', 'hi')
    self.assertEqual( [ 'foo' ], xattr.keys(tmp) )
    xattr.set_string(tmp, 'bar', '666')
    self.assertEqual( [ 'bar', 'foo' ], xattr.keys(tmp) )

  def test_set_string_get_string(self):
    tmp = self.make_temp_file()
    xattr.set_string(tmp, 'foo', 'hi')
    self.assertEqual( 'hi', xattr.get_string(tmp, 'foo') )

  def test_set_string_get_bytes(self):
    tmp = self.make_temp_file()
    xattr.set_string(tmp, 'foo', 'hi')
    self.assertEqual( 'hi'.encode('utf-8'), xattr.get_bytes(tmp, 'foo') )
    
  def test_set_bytes_get_string(self):
    tmp = self.make_temp_file()
    xattr.set_bytes(tmp, 'foo', 'hi'.encode('utf-8'))
    self.assertEqual( 'hi', xattr.get_string(tmp, 'foo') )
    
  def test_set_bytes_get_bytes(self):
    tmp = self.make_temp_file()
    data = 'hi'.encode('utf-8')
    xattr.set_bytes(tmp, 'foo', data)
    self.assertEqual( data, xattr.get_bytes(tmp, 'foo') )

  def test_remove(self):
    tmp = self.make_temp_file()
    self.assertEqual( [], xattr.keys(tmp) )
    xattr.set_string(tmp, 'foo', 'hi')
    self.assertEqual( [ 'foo' ], xattr.keys(tmp) )
    xattr.remove(tmp, 'foo')
    self.assertEqual( [], xattr.keys(tmp) )

  def test_clear(self):
    tmp = self.make_temp_file()
    self.assertEqual( [], xattr.keys(tmp) )
    xattr.set_string(tmp, 'foo', 'hi')
    xattr.set_string(tmp, 'bar', '666')
    self.assertEqual( [ 'bar', 'foo' ], xattr.keys(tmp) )
    xattr.clear(tmp)
    self.assertEqual( [], xattr.keys(tmp) )
    
if __name__ == '__main__':
  unit_test.main()
