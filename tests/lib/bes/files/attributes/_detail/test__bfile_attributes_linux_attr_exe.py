#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.docker.docker import docker
from bes.testing.unit_test_class_skip import unit_test_class_skip
from bes.system.host import host

from bfile_attributes_tester import make_test_case

if host.is_linux():
  from bes.files.attributes._detail._bfile_attributes_linux_attr_exe import _bfile_attributes_linux_attr_exe
  from bes.files.attributes.bfile_attributes import _bfile_attributes_mixin

  class _test_super_class_linux_xattr_exe(_bfile_attributes_linux_xattr_exe, _bfile_attributes_mixin):
    pass
  
  class test__bfile_attributes_linux_attr_exe(make_test_case(_test_super_class_linux_xattr_exe)):

    @classmethod
    def setUpClass(clazz):
      unit_test_class_skip.raise_skip_if_not_linux()
      docker.raise_skip_if_running_under_docker()
    
if __name__ == '__main__':
  unit_test.main()
    
