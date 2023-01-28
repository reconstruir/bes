#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs.bfile_attributes import bfile_attributes
from bes.docker.docker import docker

from _detail.bfile_attributes_tester import make_test_case

class test_bfile_attributes(make_test_case(bfile_attributes)):
  
  @classmethod
  def setUpClass(clazz):
    docker.raise_skip_if_running_under_docker()
    
if __name__ == '__main__':
  unit_test.main()
    
