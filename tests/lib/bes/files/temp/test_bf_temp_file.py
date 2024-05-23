#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import os

from bes.files.temp.bf_temp_file import bf_temp_file
from bes.files.bf_file_ops import bf_file_ops
from bes.testing.unit_test import unit_test

class test_bf_temp_file(unit_test):

  def test_make_temp_file(self):
    f = bf_temp_file.make_temp_file()
    self.assertEqual( True, path.exists(f) )
    self.assertEqual( True, path.isfile(f) )
    self.assertEqual( '', bf_file_ops.read(f, encoding = 'utf-8') )
    
  def test_make_temp_file_with_text_content(self):
    f = bf_temp_file.make_temp_file(content = 'kiwi')
    self.assertEqual( 'kiwi', bf_file_ops.read(f, encoding = 'utf-8') )

  def test_make_temp_file_with_binary_content(self):
    f = bf_temp_file.make_temp_file(content = b'deadbeaf')
    self.assertEqual( b'deadbeaf', bf_file_ops.read(f) )

  def test_make_temp_file_with_prefix(self):
    f = bf_temp_file.make_temp_file(prefix = 'kiwi-')
    self.assertEqual( True, path.basename(f).startswith('kiwi') )

  def test_make_temp_file_with_suffix(self):
    f = bf_temp_file.make_temp_file(suffix = '.txt')
    self.assertEqual( True, f.endswith('.txt') )

  def test_make_temp_file_without_create(self):
    f = bf_temp_file.make_temp_file(create = False)
    self.assertEqual( False, path.exists(f) )

  def test_make_temp_file_with_perm(self):
    f = bf_temp_file.make_temp_file(perm = 0o700)
    self.assertEqual( 0o700, os.stat(f).st_mode & 0o777 )

    f = bf_temp_file.make_temp_file(perm = 0o644)
    self.assertEqual( 0o644, os.stat(f).st_mode & 0o777 )
    
if __name__ == '__main__':
  unit_test.main()
