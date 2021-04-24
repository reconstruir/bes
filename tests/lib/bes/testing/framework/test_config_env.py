#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.system.env_override import env_override

from bes.testing.unit_test import unit_test
from bes.testing.framework.config_env import config_env as CE
from bes.docker.docker import docker
  
class test_config_env(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/lib/bes/testing/framework'

  @classmethod
  def setUpClass(clazz):
    docker.raise_skip_if_running_under_docker()
  
  def test_complete(self):
    a = CE(self.data_dir())
    print(a.dependency_map)

  def test_find_config_files(self):
    expected_files = [
      self.native_filename('citrus/env/citrus.bescfg'),
      self.native_filename('fiber/env/fiber.bescfg'),
      self.native_filename('fruit/env/fruit.bescfg'),
      self.native_filename('kiwi/env/kiwi.bescfg'),
      self.native_filename('orange/env/orange.bescfg'),
      self.native_filename('water/env/water.bescfg')
    ]
    with env_override.clean_env() as ctx:
      actual = CE._find_config_files(self.data_dir())
      expected = [ path.join(self.data_dir(), x) for x in expected_files ]
      self.assertEqual( expected, actual )
    
if __name__ == '__main__':
  unit_test.main()
    
