#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs.file_attributes import file_attributes
from bes.system.bdocker import bdocker

from _detail.file_attributes_tester import make_test_case

class test_file_attributes(make_test_case(file_attributes)):
  
  @classmethod
  def setUpClass(clazz):
    bdocker.raise_skip_if_running_under_docker()
    
if __name__ == '__main__':
  unit_test.main()
    
