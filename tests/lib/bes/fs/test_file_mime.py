#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, sys
from os import path

from bes.testing.unit_test import unit_test
from bes.fs.file_mime import file_mime
from bes.fs.file_symlink import file_symlink
from bes.testing.unit_test_skip import skip_if_not_unix, skip_if_not_windows

class test_file_mime(unit_test):

  def test_mime_type(self):
    tmp = self.make_temp_file(content = 'this is text\n', suffix = '.txt')
    mt = file_mime.mime_type(tmp)
    self.assertEqual( 'text/plain', mt.mime_type )
    if mt.charset:
      self.assertEqual( 'us-ascii', mt.charset )

  def test_is_false(self):
    self.assertFalse( file_mime.is_binary(self.make_temp_file(content = 'this is text\n', suffix = '.txt')) )
    
  @skip_if_not_unix()
  def test_is_binary_unix(self):
    self.assertTrue( file_mime.is_binary(file_symlink.resolve('/bin/sh')) )
    
  @skip_if_not_windows()
  def test_is_binary_windows(self):
    self.assertTrue( file_mime.is_text(sys.executable) )
    
  def test_is_text(self):
    self.assertTrue( file_mime.is_text(self.make_temp_file(content = 'this is text\n', suffix = '.txt')) )

  @skip_if_not_unix()
  def test_is_text_false_unix(self):
    self.assertFalse( file_mime.is_text(file_symlink.resolve('/bin/sh')) )

if __name__ == '__main__':
  unit_test.main()
