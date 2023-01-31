#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.files.attributes.bfile_cached_attr import bfile_cached_attr
from bes.docker.docker import docker

from _detail.bfile_cached_attr_tester import make_test_case

class test_bfile_cached_attr(make_test_case(bfile_cached_attr)):
  
  @classmethod
  def setUpClass(clazz):
    docker.raise_skip_if_running_under_docker()
    
if __name__ == '__main__':
  unit_test.main()
