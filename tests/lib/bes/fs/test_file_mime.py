#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import binascii, os, sys
from os import path

from bes.testing.unit_test import unit_test
from bes.fs.file_mime import file_mime
from bes.fs.file_symlink import file_symlink
from bes.testing.unit_test_skip import skip_if_not_unix, skip_if_not_windows

class test_file_mime(unit_test):

  # 1x1 PNG file
  _TEST_DATA_PNG = '89504e470d0a1a0a0000000d4948445200000001000000010802000000907753de00000184694343504943432070726f66696c65000028917d913d48c3401886dfa68a452a22161471c8509d2c888a386a158a5021d40aad3a985cfa074d1a92141747c1b5e0e0cf62d5c1c5595707574110fc0171727452749112bf4b0a2d62bce3b887f7bef7e5ee3b40a8979966758c039a6e9ba9445ccc6457c5ae5784d087019a82cc2c634e9292f01d5ff708f0fd2ec6b3fcebfe1c3d6ace624040249e658669136f104f6fda06e77de2082bca2af139f1984917247ee4bae2f11be782cb02cf8c98e9d43c7184582cb4b1d2c6ac686ac453c45155d3295fc878ac72dee2ac95abac794ffec2704e5f59e63aad6124b088254810a1a08a12cab011a35d27c5428acee33efe21d72f914b2157098c1c0ba84083ecfac1ffe0776fadfce48497148e039d2f8ef3310274ed028d9ae37c1f3b4ee304083e03577acb5fa903339fa4d75a5af408e8dd062eae5b9ab2075cee00834f866ccaae14a425e4f3c0fb197d5316e8bf05bad7bcbe35cf71fa00a4a957c91be0e010182d50f6bacfbb43ed7dfbb7a6d9bf1f20f472864f68cb260000000970485973000021380000213801459631600000000774494d4507e40812121d17e87cb9240000000c4944415408d763f8ffff3f0005fe02fedccc59e70000000049454e44ae426082'
  _TEST_DATA_BYTES = binascii.unhexlify(_TEST_DATA_PNG)
  
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

  def test_content_is_text_true(self):
    self.assertTrue( file_mime.content_is_text(self.make_temp_file(content = 'this is text\n', suffix = '.txt')) )
    
  def test_content_is_text_false(self):
    self.assertFalse( file_mime.content_is_text(self.make_temp_file(content = self._TEST_DATA_BYTES, suffix = '.png')) )
    
  @skip_if_not_unix()
  def test_is_text_false_unix(self):
    self.assertFalse( file_mime.is_text(file_symlink.resolve('/bin/sh')) )

if __name__ == '__main__':
  unit_test.main()
