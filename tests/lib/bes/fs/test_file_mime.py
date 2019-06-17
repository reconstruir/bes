#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path
import unittest
from bes.fs.file_mime import file_mime

class test_file_mime(unittest.TestCase):

  def test_mime_type(self):
    mt = file_mime.mime_type('/etc/passwd')
    self.assertEqual( ( 'text/plain', 'us-ascii' ), mt )
    self.assertEqual( 'text/plain; charset=us-ascii', str(mt) )

  @classmethod
  def _find_binary_file(clazz):
    possible = [
      '/bin/bash',
      '/bin/sh',
      '/bin/busybox',
    ]
    for f in possible:
      if path.isfile(f):
        return f
    return None
    
  def test_shell_is_binary(self):
    f = self._find_binary_file()
    self.assertTrue( file_mime.mime_type(f).mime_type in file_mime.BINARY_TYPES )

  def test_is_text(self):
    self.assertTrue( file_mime.is_text('/etc/passwd') )
    f = self._find_binary_file()
    self.assertFalse( file_mime.is_text(f) )

if __name__ == "__main__":
  unittest.main()
