#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.files.attr2.bf_attr2 import bf_attr2
from bes.docker.docker import docker

from _detail._bf_attr2_unit_test_common import make_test_case

class test_bf_attr2(make_test_case(bf_attr2)):
  
  @classmethod
  def setUpClass(clazz):
    docker.raise_skip_if_running_under_docker()
    
if __name__ == '__main__':
  unit_test.main()
