#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import binascii
import os.path as path

from bes.testing.unit_test import unit_test
from bes.fs.file_attributes import file_attributes
from bes.fs.file_attributes import HAS_XATTR
from bes.fs.file_util import file_util
from bes.system.bdocker import bdocker
from bes.testing.unit_test_class_skip import unit_test_class_skip
from bes.system.host import host

from file_attributes_tester import make_test_case

if host.is_linux():
  from bes.fs._detail._file_attributes_linux_attr_exe import _file_attributes_linux_attr_exe
  class test__file_attributes_linux_attr_exe(make_test_case(_file_attributes_linux_attr_exe)):

    @classmethod
    def setUpClass(clazz):
      unit_test_class_skip.raise_skip_if_not_linux()
      bdocker.raise_skip_if_running_under_docker()
    
if __name__ == '__main__':
  unit_test.main()
    
