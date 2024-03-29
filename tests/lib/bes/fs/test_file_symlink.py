#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, tempfile
from bes.testing.unit_test import unit_test
from bes.fs.file_symlink import file_symlink
from bes.fs.file_util import file_util
from bes.testing.unit_test_class_skip import unit_test_class_skip

class test_file_symlink(unit_test):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip_if(file_symlink.has_support(), 'No support or priviledge for symlinks')
  
  def test_is_broken_true(self):
    tmp = tempfile.NamedTemporaryFile()
    file_util.remove(tmp.name)
    os.symlink('/somethingnotthere', tmp.name)
    self.assertEqual( True, path.islink(tmp.name) )
    self.assertEqual( True, file_symlink.is_broken(tmp.name) )

  def test_is_broken_false(self):
    tmp1 = tempfile.NamedTemporaryFile()
    tmp2 = tempfile.NamedTemporaryFile()
    file_util.remove(tmp1.name)
    os.symlink(tmp2.name, tmp1.name)
    self.assertEqual( True, path.islink(tmp1.name) )
    self.assertEqual( False, file_symlink.is_broken(tmp1.name) )

  def test_resolve_one_level(self):
    tmp1 = self.make_temp_file(suffix = '-one')
    tmp2 = self.make_temp_file(suffix = '-two')
    file_util.remove(tmp2)
    os.symlink(tmp1, tmp2)
    self.assertEqual( tmp1, file_symlink.resolve(tmp1) )
    self.assertEqual( tmp1, file_symlink.resolve(tmp2) )

  def test_resolve_two_levels(self):
    tmp1 = self.make_temp_file()
    tmp2 = self.make_temp_file()
    tmp3 = self.make_temp_file()
    file_util.remove(tmp2)
    file_util.remove(tmp3)
    os.symlink(tmp1, tmp2)
    os.symlink(tmp2, tmp3)
    self.assertEqual( tmp1, file_symlink.resolve(tmp1) )
    self.assertEqual( tmp1, file_symlink.resolve(tmp2) )
    self.assertEqual( tmp1, file_symlink.resolve(tmp3) )

  def test_resolve_cyclic_error(self):
    tmp1 = self.make_temp_file(suffix = '-one')
    tmp2 = self.make_temp_file(suffix = '-two')
    file_util.remove(tmp2)
    os.symlink(tmp1, tmp2)
    file_util.remove(tmp1)
    os.symlink(tmp2, tmp1)
    with self.assertRaises(IOError) as ctx:
      file_symlink.resolve(tmp1)
    self.assertTrue( 'Cyclic error' in str(ctx.exception) )
      
    
if __name__ == '__main__':
  unit_test.main()
