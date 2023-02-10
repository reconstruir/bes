#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.testing.unit_test_class_skip import unit_test_class_skip

from _bfile_mime_type_detector_tester import make_test_case

from bes.files.mime._detail._bfile_mime_type_detector_mimetypes import _bfile_mime_type_detector_mimetypes
class test__bfile_mime_type_detector_mimetypes(make_test_case(_bfile_mime_type_detector_mimetypes)):
  pass

if __name__ == '__main__':
  unit_test.main()
    
