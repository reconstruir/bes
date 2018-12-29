#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.fs import file_mime

class test_file_mime(unittest.TestCase):

  def test_mime_type(self):
    mt = file_mime.mime_type('/etc/passwd')
    self.assertEqual( ( 'text/plain', 'us-ascii' ), mt )
    self.assertEqual( 'text/plain; charset=us-ascii', str(mt) )

  def test_ls_is_binary(self):
    self.assertTrue( file_mime.mime_type('/bin/ls').mime_type in file_mime.BINARY_TYPES )

  def test_is_text(self):
    self.assertTrue( file_mime.is_text('/etc/passwd') )
    self.assertFalse( file_mime.is_text('/bin/ls') )

  def test__parse_file_output_fat(self):
    text = '''\
./tests/test_data/binary_objects/macos/fat_32_obj.o (for architecture i386):	application/x-mach-binary; charset=binary
./tests/test_data/binary_objects/macos/fat_32_obj.o (for architecture armv7):	application/x-mach-binary; charset=binary; charset=binary
'''
    self.assertEqual( ( 'application/x-mach-binary', 'binary' ),
                      file_mime._parse_file_output(text) )
    
  def test__parse_file_output_non_fat(self):
    text = '''application/x-mach-binary; charset=binary'''
    self.assertEqual( ( 'application/x-mach-binary', 'binary' ),
                      file_mime._parse_file_output(text) )
    
  def test__parse_file_output_non_fatPdupl_charset(self):
    text = '''application/x-mach-binary; charset=binary; charset=binary'''
    self.assertEqual( ( 'application/x-mach-binary', 'binary' ),
                      file_mime._parse_file_output(text) )
    
    
if __name__ == "__main__":
  unittest.main()
