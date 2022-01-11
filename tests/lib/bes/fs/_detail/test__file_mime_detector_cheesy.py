#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs._detail._file_mime_type_detector_cheesy import _file_mime_type_detector_cheesy
from bes.testing.unit_test_class_skip import unit_test_class_skip

from _file_mime_type_detector_tester import make_test_case

class test__file_mime_type_detector_magic(make_test_case(_file_mime_type_detector_cheesy)):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip_if(_file_mime_type_detector_cheesy.is_supported(), 'not supported')

if __name__ == '__main__':
  unit_test.main()
    
