#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.testing.unit_test_class_skip import unit_test_class_skip
from bes.system.host import host

from _bfile_mime_type_detector_tester import make_test_case

from bes.files.mime._detail._bfile_mime_type_detector_puremagic import _bfile_mime_type_detector_puremagic
class test__bfile_mime_type_detector_puremagic(make_test_case(_bfile_mime_type_detector_puremagic)):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip_if(_bfile_mime_type_detector_puremagic.is_supported(), 'puremagic not found')

  def test_text_plain(self):
    tmp = self.make_temp_file(content = 'this is text\n', suffix = '.txt')

    #self.assertEqual( None, _bfile_mime_type_detector_puremagic.detect_mime_type(tmp) )
    self.assertEqual( 'text/plain', _bfile_mime_type_detector_puremagic.detect_mime_type(tmp) )
      
if __name__ == '__main__':
  unit_test.main()
    
