#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.testing.unit_test_class_skip import unit_test_class_skip
from bes.system.host import host

from _bfile_mime_type_detector_tester import make_test_case

if host.is_unix():
  from bes.fs._detail._bfile_mime_type_detector_file_exe import _bfile_mime_type_detector_file_exe
  class test__bfile_mime_type_detector_file_exe(make_test_case(_bfile_mime_type_detector_file_exe)):

    @classmethod
    def setUpClass(clazz):
      unit_test_class_skip.raise_skip_if_not_unix()

if __name__ == '__main__':
  unit_test.main()
    
