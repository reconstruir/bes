#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, sys
from os import path

from bes.testing.unit_test import unit_test
from bes.fs.file_mime import file_mime

class test_file_mime(unit_test):

  def test_mime_type(self):
    tmp = self.make_temp_file(content = 'this is text\n', suffix = '.txt')
    mt = file_mime.mime_type(tmp)
    self.assertEqual( 'text/plain', mt.mime_type )
    if mt.charset:
      self.assertEqual( 'us-ascii', mt.charset )

  def test_is_binary(self):
    self.assertTrue( file_mime.is_binary(sys.executable) )
    self.assertFalse( file_mime.is_binary(self.make_temp_file(content = 'this is text\n', suffix = '.txt')) )
    
  def test_is_text(self):
    self.assertFalse( file_mime.is_text(sys.executable) )
    self.assertTrue( file_mime.is_text(self.make_temp_file(content = 'this is text\n', suffix = '.txt')) )

if __name__ == '__main__':
  unit_test.main()
