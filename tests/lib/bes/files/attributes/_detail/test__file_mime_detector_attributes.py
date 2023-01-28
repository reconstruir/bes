#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.testing.unit_test_class_skip import unit_test_class_skip

from _file_mime_type_detector_tester import make_test_case

from bes.fs._detail._file_mime_type_detector_attributes import _file_mime_type_detector_attributes
class test__file_mime_type_detector_attributes(make_test_case(_file_mime_type_detector_attributes)):
  pass

if __name__ == '__main__':
  unit_test.main()
    
