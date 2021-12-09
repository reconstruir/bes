#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.macos.xattr.xattr import xattr

class test_xattr(unit_test):

  def test_keys(self):
    tmp = self.make_temp_file()
    self.assertEqual( [], xattr.keys(tmp) )

  def test_set_string_get_string(self):
    tmp = self.make_temp_file()
    xattr.set_string(tmp, 'foo', 'hi')
    self.assertEqual( 'hi', xattr.get_string(tmp, 'foo') )
    
if __name__ == '__main__':
  unit_test.main()
