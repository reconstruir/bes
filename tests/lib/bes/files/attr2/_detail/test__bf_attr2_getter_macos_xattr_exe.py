#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.docker.docker import docker
from bes.testing.unit_test_class_skip import unit_test_class_skip
from bes.system.host import host

from _bf_attr2_unit_test_common import make_test_case
    
if host.is_macos():
  from bes.files.attr2._detail._bf_attr2_getter_macos_xattr_exe import _bf_attr2_getter_macos_xattr_exe
  from bes.files.attr2.bf_attr2 import _bf_attr2_mixin

  class _test_super_class_macos_xattr_exe(_bf_attr2_getter_macos_xattr_exe, _bf_attr2_mixin):
    pass
  
  class test__bf_attr2_getter_macos_xattr_exe(make_test_case(_test_super_class_macos_xattr_exe())):

    @classmethod
    def setUpClass(clazz):
      unit_test_class_skip.raise_skip_if_not_macos()
      docker.raise_skip_if_running_under_docker()
    
if __name__ == '__main__':
  unit_test.main()
    
