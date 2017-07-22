#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import unittest
from bes.fs import file_type

class test_file_type(unittest.TestCase):

  # Darwin and Linux are different
  EXECUTABLE_TYPES = [
    'application/octet-stream; charset=binary',
    'application/x-executable; charset=binary',
  ]
  
  def test_mime_type(self):
    self.assertEqual( 'text/plain; charset=us-ascii', file_type.mime_type('/etc/passwd') )
    self.assertTrue( file_type.mime_type('/bin/ls') in file_type.BINARY_TYPES )

  def test_is_text(self):
    self.assertTrue( file_type.is_text('/etc/passwd') )
    self.assertFalse( file_type.is_text('/bin/ls') )

  def test_is_binary(self):
    self.assertFalse( file_type.is_binary('/etc/passwd') )
    self.assertTrue( file_type.is_binary('/bin/ls') )

if __name__ == "__main__":
  unittest.main()
