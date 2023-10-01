#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, unittest

from bes.fs.file_util import file_util
from bes.system.env_override import env_override
from bes.system.host import host
from bes.system.filesystem import filesystem
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

class test_filesystem(unit_test):
    
#  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')

  def test_remove_file(self):
    tmp_file = self.make_temp_file()
    self.assertEqual( True, path.exists(tmp_file) )
    filesystem.remove(tmp_file)
    self.assertEqual( False, path.exists(tmp_file) )

  def test_remove_file_not_found(self):
    tmp_file = self.make_temp_file(perm = 0o000)
    self.assertEqual( True, path.exists(tmp_file) )
    filesystem.remove(tmp_file)
    self.assertEqual( False, path.exists(tmp_file) )
    filesystem.remove(tmp_file)

  def test_remove_file_not_found_with_raise(self):
    tmp_file = self.make_temp_file(perm = 0o000)
    self.assertEqual( True, path.exists(tmp_file) )
    filesystem.remove(tmp_file)
    self.assertEqual( False, path.exists(tmp_file) )
    with self.assertRaises(FileNotFoundError) as _:
      filesystem.remove(tmp_file, raise_not_found_error = True)
    
  def test_remove_dir(self):
    tmp_dir = self.make_temp_dir()
    self.assertEqual( True, path.exists(tmp_dir) )
    filesystem.remove(tmp_dir)
    self.assertEqual( False, path.exists(tmp_dir) )
    
if __name__ == '__main__':
  unit_test.main()
