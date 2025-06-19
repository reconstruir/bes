#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.files.attr._detail._bf_attr_getter_super_class import HAS_XATTR
from bes.files.attr._detail._bf_attr_getter_super_class import HAS_XATTR
from bes.system.bdocker import bdocker
from bes.testing.unit_test_class_skip import unit_test_class_skip
from bes.system.host import host

from _bf_attr_unit_test_common import make_test_case

if HAS_XATTR:
  from bes.files.attr._detail._bf_attr_getter_xattr import _bf_attr_getter_xattr
  
  class test__bf_attr_getter_xattr(make_test_case(_bf_attr_getter_xattr())):

    @classmethod
    def setUpClass(clazz):
      unit_test_class_skip.raise_skip_if_not_unix()
      unit_test_class_skip.raise_skip_if(HAS_XATTR, 'xattr not found')
      bdocker.raise_skip_if_running_under_docker()
    
if __name__ == '__main__':
  unit_test.main()
    
