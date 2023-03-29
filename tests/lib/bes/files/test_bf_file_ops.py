#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, tempfile
from datetime import datetime
from datetime import timedelta

from bes.testing.unit_test import unit_test
from bes.files.bf_file_ops import bf_file_ops
from bes.common.hash_util import hash_util

class test_bf_file_ops(unit_test):

  def test_files_are_the_same_true(self):
    f1 = self.make_temp_file(content = f'abcdefghijklmnopqrstuvwxyz')
    f2 = self.make_temp_file(content = f'abcdefghijklmnopqrstuvwxyz')
    self.assertEqual( True, bf_file_ops.files_are_the_same(f1, f2) )

  def test_files_are_the_same_false(self):
    f1 = self.make_temp_file(content = f'abcdefghijklmnopqrstuvwxyz')
    f2 = self.make_temp_file(content = f'abcdefghijklmnopqrstuvwxy')
    self.assertEqual( False, bf_file_ops.files_are_the_same(f1, f2) )

  def test_save_non_existent_no_content(self):
    tmp = self.make_temp_file(non_existent = True)
    self.assertEqual( False, path.exists(tmp) )
    bf_file_ops.save(tmp)
    self.assertEqual( True, path.exists(tmp) )

  def test_save_existing_no_content(self):
    tmp = self.make_temp_file(non_existent = False)
    self.assertEqual( True, path.exists(tmp) )
    bf_file_ops.save(tmp)
    self.assertEqual( True, path.exists(tmp) )

  def test_save_non_existent_with_content_string(self):
    tmp = self.make_temp_file(non_existent = True)
    content = 'kiwi'
    bf_file_ops.save(tmp, content = content)
    with open(tmp, 'r') as f:
      self.assertEqual( content, f.read() )

  def test_save_non_existent_with_content_bytes(self):
    tmp = self.make_temp_file(non_existent = True)
    content = b'\x31\x42\x59\x26\x53\x58'
    bf_file_ops.save(tmp, content = content)
    with open(tmp, 'rb') as f:
      self.assertEqual( content, f.read() )

  def test_save_non_existent_with_content_invalid(self):
    tmp = self.make_temp_file(non_existent = True)
    with self.assertRaises(TypeError) as _:
      bf_file_ops.save(tmp, content = 42)
      
if __name__ == '__main__':
  unit_test.main()
