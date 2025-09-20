#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, tempfile
from bes.testing.unit_test import unit_test
from bes.files.bf_symlink import bf_symlink
from bes.files.core.bf_error import bf_error
from bes.system.filesystem import filesystem

from bes.testing.unit_test_class_skip import unit_test_class_skip

class test_bf_symlink(unit_test):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip_if(bf_symlink.has_support(), 'No support or priviledge for symlinks')
  
  def test_is_broken_true(self):
    tmp = tempfile.NamedTemporaryFile()
    filesystem.remove(tmp.name)
    os.symlink('/somethingnotthere', tmp.name)
    self.assertEqual( True, path.islink(tmp.name) )
    self.assertEqual( True, bf_symlink.is_broken(tmp.name) )

  def test_is_broken_false(self):
    tmp1 = tempfile.NamedTemporaryFile()
    tmp2 = tempfile.NamedTemporaryFile()
    filesystem.remove(tmp1.name)
    os.symlink(tmp2.name, tmp1.name)
    self.assertEqual( True, path.islink(tmp1.name) )
    self.assertEqual( False, bf_symlink.is_broken(tmp1.name) )

  def test_resolve_one_level(self):
    tmp1 = self.make_temp_file(suffix = '-one')
    tmp2 = self.make_temp_file(suffix = '-two')
    filesystem.remove(tmp2)
    os.symlink(tmp1, tmp2)
    self.assertEqual( tmp1, bf_symlink.resolve(tmp1) )
    self.assertEqual( tmp1, bf_symlink.resolve(tmp2) )

  def test_resolve_two_levels(self):
    tmp1 = self.make_temp_file()
    tmp2 = self.make_temp_file()
    tmp3 = self.make_temp_file()
    filesystem.remove(tmp2)
    filesystem.remove(tmp3)
    os.symlink(tmp1, tmp2)
    os.symlink(tmp2, tmp3)
    self.assertEqual( tmp1, bf_symlink.resolve(tmp1) )
    self.assertEqual( tmp1, bf_symlink.resolve(tmp2) )
    self.assertEqual( tmp1, bf_symlink.resolve(tmp3) )

  def test_resolve_cyclic_error(self):
    tmp1 = self.make_temp_file(suffix = '-one')
    tmp2 = self.make_temp_file(suffix = '-two')
    filesystem.remove(tmp2)
    os.symlink(tmp1, tmp2)
    filesystem.remove(tmp1)
    os.symlink(tmp2, tmp1)
    with self.assertRaises(bf_error) as ctx:
      bf_symlink.resolve(tmp1)
    self.assertTrue( 'Cyclic error' in str(ctx.exception) )
    
if __name__ == '__main__':
  unit_test.main()
