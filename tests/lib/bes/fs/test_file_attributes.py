#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import binascii
import os.path as path

from bes.testing.unit_test import unit_test
from bes.fs.file_attributes import file_attributes
from bes.fs.file_attributes import HAS_XATTR
from bes.fs.file_util import file_util
from bes.docker.docker import docker
from bes.testing.unit_test_class_skip import unit_test_class_skip
from bes.system.host import host

from _detail.file_attributes_tester import make_test_case

class test_file_attributes(make_test_case(file_attributes)):
  
  @classmethod
  def setUpClass(clazz):
    docker.raise_skip_if_running_under_docker()

if host.is_macos():
  from bes.fs._detail._file_attributes_macos import _file_attributes_macos
  class test__file_attributes_macos(make_test_case(_file_attributes_macos)):

    @classmethod
    def setUpClass(clazz):
      unit_test_class_skip.raise_skip_if_not_macos()
      docker.raise_skip_if_running_under_docker()

if host.is_linux():
  from bes.fs._detail._file_attributes_linux import _file_attributes_linux
  class test__file_attributes_linux(make_test_case(_file_attributes_linux)):

    @classmethod
    def setUpClass(clazz):
      unit_test_class_skip.raise_skip_if_not_linux()
      docker.raise_skip_if_running_under_docker()

if host.is_windows():    
  from bes.fs._detail._file_attributes_windows import _file_attributes_windows
  class test__file_attributes_windows(make_test_case(_file_attributes_windows)):

    @classmethod
    def setUpClass(clazz):
      unit_test_class_skip.raise_skip_if_not_windows()
      docker.raise_skip_if_running_under_docker()

if HAS_XATTR:
  from bes.fs._detail._file_attributes_xattr import _file_attributes_xattr
  class test__file_attributes_xattr(make_test_case(_file_attributes_xattr)):

    @classmethod
    def setUpClass(clazz):
      unit_test_class_skip.raise_skip_if_not_unix()
      unit_test_class_skip.raise_skip_if(HAS_XATTR, 'xattr not found')
      docker.raise_skip_if_running_under_docker()
    
if __name__ == '__main__':
  unit_test.main()
    
