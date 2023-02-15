#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.testing.unit_test_class_skip import unit_test_class_skip

from _bfile_mime_type_detector_tester import make_test_case

from bes.fs._detail._bfile_mime_type_detector_magic import _bfile_mime_type_detector_magic
class test__bfile_mime_type_detector_magic(make_test_case(_bfile_mime_type_detector_magic)):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip_if(_bfile_mime_type_detector_magic.is_supported(), 'not supported')

if __name__ == '__main__':
  unit_test.main()
    
