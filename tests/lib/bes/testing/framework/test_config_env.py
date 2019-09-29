#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.system.env_override import env_override

from bes.testing.unit_test import unit_test
from bes.testing.framework.config_env import config_env as CE
  
class test_config_env(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/lib/bes/testing/framework'
  
  def test_complete(self):
    a = CE(self.data_dir())
    print(a.dependency_map)

  def test_find_config_files(self):
    expected_files = [
      self.p('citrus/env/citrus.bescfg'),
      self.p('fiber/env/fiber.bescfg'),
      self.p('fruit/env/fruit.bescfg'),
      self.p('kiwi/env/kiwi.bescfg'),
      self.p('orange/env/orange.bescfg'),
      self.p('water/env/water.bescfg')
    ]
    with env_override.clean_env() as ctx:
      actual = CE._find_config_files(self.data_dir())
      expected = [ path.join(self.data_dir(), x) for x in expected_files ]
      self.assertEqual( expected, actual )
    
if __name__ == '__main__':
  unit_test.main()
    
