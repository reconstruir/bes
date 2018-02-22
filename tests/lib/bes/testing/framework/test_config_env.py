#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.testing.framework import config_env as CE
  
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
    files = CE.find_config_files(self.data_dir())
    self.assertEqual( [ path.join(self.data_dir(), x) for x in expected_files ],
                      files )
    
if __name__ == '__main__':
  unit_test.main()
    
