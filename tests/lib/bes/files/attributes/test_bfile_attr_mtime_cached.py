#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.files.attributes.bfile_attr_mtime_cached import bfile_attr_mtime_cached
from bes.docker.docker import docker

from _detail._bfile_attr_mtime_cached_unit_test_common import make_test_case

class test_bfile_attr_mtime_cached(make_test_case(bfile_attr_mtime_cached)):
  
  @classmethod
  def setUpClass(clazz):
    docker.raise_skip_if_running_under_docker()
    
if __name__ == '__main__':
  unit_test.main()
