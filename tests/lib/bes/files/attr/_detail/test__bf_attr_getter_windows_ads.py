#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.docker.docker import docker
from bes.testing.unit_test_class_skip import unit_test_class_skip
from bes.system.host import host

from _bf_attr_unit_test_common import make_test_case

if host.is_windows():
  from bes.files.attr._detail._bf_attr_getter_windows_ads import _bf_attr_getter_windows_ads

  class test__bf_attr_getter_windows_ads(make_test_case(_bf_attr_getter_windows_ads())):

    @classmethod
    def setUpClass(clazz):
      unit_test_class_skip.raise_skip_if_not_windows()
      docker.raise_skip_if_running_under_docker()
    
if __name__ == '__main__':
  unit_test.main()
    
