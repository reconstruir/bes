#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.macos.xattr_exe.xattr_exe import xattr_exe
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_class_skip import unit_test_class_skip

from _bes_unit_test_common.unit_test_media import unit_test_media

class test_xattr_exe(unit_test):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip_if_not_macos()
  
  def test_has_key(self):
    tmp = self.make_temp_file()
    self.assertFalse( xattr_exe.has_key(tmp, 'foo') )
    xattr_exe.set_string(tmp, 'foo', 'hi')
    self.assertTrue( xattr_exe.has_key(tmp, 'foo') )
  
  def test_keys(self):
    tmp = self.make_temp_file()
    self.assertEqual( [], xattr_exe.keys(tmp) )
    xattr_exe.set_string(tmp, 'foo', 'hi')
    self.assertEqual( [ 'foo' ], xattr_exe.keys(tmp) )
    xattr_exe.set_string(tmp, 'bar', '666')
    self.assertEqual( [ 'bar', 'foo' ], xattr_exe.keys(tmp) )

  def test_set_string_get_string(self):
    tmp = self.make_temp_file()
    xattr_exe.set_string(tmp, 'foo', 'hi')
    self.assertEqual( 'hi', xattr_exe.get_string(tmp, 'foo') )

  def test_set_string_get_bytes(self):
    tmp = self.make_temp_file()
    xattr_exe.set_string(tmp, 'foo', 'hi')
    self.assertEqual( 'hi'.encode('utf-8'), xattr_exe.get_bytes(tmp, 'foo') )
    
  def test_set_bytes_get_string(self):
    tmp = self.make_temp_file()
    xattr_exe.set_bytes(tmp, 'foo', 'hi'.encode('utf-8'))
    self.assertEqual( 'hi', xattr_exe.get_string(tmp, 'foo') )
    
  def test_set_bytes_get_bytes(self):
    tmp = self.make_temp_file()
    data = 'hi'.encode('utf-8')
    xattr_exe.set_bytes(tmp, 'foo', data)
    self.assertEqual( data, xattr_exe.get_bytes(tmp, 'foo') )

  def test_remove(self):
    tmp = self.make_temp_file()
    self.assertEqual( [], xattr_exe.keys(tmp) )
    xattr_exe.set_string(tmp, 'foo', 'hi')
    self.assertEqual( [ 'foo' ], xattr_exe.keys(tmp) )
    xattr_exe.remove(tmp, 'foo')
    self.assertEqual( [], xattr_exe.keys(tmp) )

  def test_clear(self):
    tmp = self.make_temp_file()
    self.assertEqual( [], xattr_exe.keys(tmp) )
    xattr_exe.set_string(tmp, 'foo', 'hi')
    xattr_exe.set_string(tmp, 'bar', '666')
    self.assertEqual( [ 'bar', 'foo' ], xattr_exe.keys(tmp) )
    xattr_exe.clear(tmp)
    self.assertEqual( [], xattr_exe.keys(tmp) )

  def test_set_png_get_png(self):
    tmp = self.make_temp_file()
    xattr_exe.set_bytes(tmp, 'picture', unit_test_media.PNG_SMALLEST_POSSIBLE)
    self.assertEqual( unit_test_media.PNG_SMALLEST_POSSIBLE, xattr_exe.get_bytes(tmp, 'picture') )
    
if __name__ == '__main__':
  unit_test.main()
