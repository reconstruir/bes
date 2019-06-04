#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.system.env_override import env_override

from bes.testing.unit_test import unit_test
from bes.testing.framework.config_env import config_env as CE
  
class test_config_env(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/bes.testing/framework'
  
  def test_complete(self):
    a = CE(self.data_dir())
    print(a.dependency_map)

  def test_find_config_files(self):
    expected_files = [
      'citrus/env/citrus.bescfg',
      'fiber/env/fiber.bescfg',
      'fruit/env/fruit.bescfg',
      'kiwi/env/kiwi.bescfg',
      'orange/env/orange.bescfg',
      'water/env/water.bescfg'
    ]
    with env_override.clean_env() as ctx:
      actual = CE._find_config_files(self.data_dir())
      expected = [ path.join(self.data_dir(), x) for x in expected_files ]

      for x in expected:
        print('EXPECTED: {}'.format(x))

      for x in actual:
        print('  ACTUAL: {}'.format(x))
      
      self.assertEqual( expected, actual )
    
if __name__ == '__main__':
  unit_test.main()
    
