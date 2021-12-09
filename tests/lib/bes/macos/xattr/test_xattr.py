#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.macos.xattr.xattr import xattr

class test_xattr(unit_test):

  def test_foo(self):
    tmp = self.make_temp_file()
    self.assertEqual( [], xattr.keys(tmp) )
    
if __name__ == '__main__':
  unit_test.main()
