#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.system.env_override import env_override

from bes.testing.unit_test import unit_test
from bes.testing.framework.config_env import config_env
from bes.docker.docker import docker

from example_data import example_data

class test_config_env(unit_test):

  @classmethod
  def setUpClass(clazz):
    docker.raise_skip_if_running_under_docker()
  
  def xtest_dependency_map(self):
    tmp_dir = example_data.make_temp_content(delete = not self.DEBUG)
    a = config_env(tmp_dir)
    self.assertEqual( {
      'citrus': set(),
      'fiber': set(),
      'fruit': {'water'},
      'kiwi': {'fruit'},
      'orange': {'fruit', 'citrus'},
      'water': set()
    }, a.dependency_map )

  def test_find_config_files(self):
    tmp_dir = example_data.make_temp_content(delete = not self.DEBUG)
    expected_files = [
      self.native_filename('citrus/env/citrus.bescfg'),
      self.native_filename('fiber/env/fiber.bescfg'),
      self.native_filename('fruit/env/fruit.bescfg'),
      self.native_filename('kiwi/env/kiwi.bescfg'),
      self.native_filename('orange/env/orange.bescfg'),
      self.native_filename('water/env/water.bescfg')
    ]
    with env_override.clean_env() as ctx:
      actual = config_env._find_config_files(tmp_dir)
      expected = [ path.join(tmp_dir, x) for x in expected_files ]
      self.assertEqual( expected, actual )
    
if __name__ == '__main__':
  unit_test.main()
    
