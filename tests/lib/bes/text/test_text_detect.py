#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.text.text_detect import text_detect

from _bes_unit_test_common.unit_test_media_files import unit_test_media_files

class test_text_detect(unit_test, unit_test_media_files):

  def test_file_is_text_true(self):
    self.assertTrue( text_detect.file_is_text(self.make_temp_file(content = 'this is text\n', suffix = '.txt')) )

  def test_file_is_text_false(self):
    self.assertFalse( text_detect.file_is_text(self.png_file) )
    
if __name__ == '__main__':
  unit_test.main()
