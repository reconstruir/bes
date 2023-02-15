#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.files.metadata.bfile_metadata import bfile_metadata
from bes.docker.docker import docker

from _detail._bfile_metadata_unit_test_common import make_test_case

class test_bfile_metadata(make_test_case(bfile_metadata)):
  
  @classmethod
  def setUpClass(clazz):
    docker.raise_skip_if_running_under_docker()
    
if __name__ == '__main__':
  unit_test.main()
