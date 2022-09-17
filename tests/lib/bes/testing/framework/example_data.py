#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.fs.testing.temp_content import temp_content

class example_data(object):

  @classmethod
  def make_temp_content(clazz, delete = True):
    return temp_content.write_items_to_temp_dir(clazz._ITEMS, delete = delete)

  # ./citrus/env/citrus.bescfg
  CITRUS__ENV__CITRUS_DOT_BESCFG = '''\
# citrus
name: citrus
unixpath: ${root_dir}/bin
pythonpath: ${root_dir}/lib
requires:
'''
  # ./fruit/env/fruit.bescfg
  FRUIT__ENV__FRUIT_DOT_BESCFG = '''\
# fruit
name: fruit
unixpath: ${root_dir}/bin
pythonpath: ${root_dir}/lib
requires: water

'''
  # ./kiwi/env/kiwi.bescfg
  KIWI__ENV__KIWI_DOT_BESCFG = '''\
# kiwi
name: kiwi
unixpath: ${root_dir}/bin
pythonpath: ${root_dir}/lib
requires: fruit
'''
  # ./water/tests/lib/water/common/test_water_util.py
  WATER__TESTS__LIB__WATER__COMMON__TEST_WATER_UTIL_DOT_PY = '''\
#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

try:
  import pytest
  pytest.skip('does not work under pytest', allow_module_level = True)
except Exception as ex:
  pass

import unittest
from water.common import water_util

class test_water_util(unittest.TestCase):

  def test_water_func_one(self):
    self.assertEqual( '666', water_util.water_func_one('666') )
  
  def test_water_func_two(self):
    self.assertEqual( '666', water_util.water_func_two('666') )
  
  def test_water_util_a_one(self):
    self.assertEqual( '666', water_util.water_util_a_one('666') )

  def test_water_util_b_one(self):
    self.assertEqual( '666', water_util.water_util_b_one('666') )

if __name__ == '__main__':
  unittest.main()
'''
  # ./water/env/water.bescfg
  WATER__ENV__WATER_DOT_BESCFG = '''\
# water
name: water
unixpath: ${root_dir}/bin
pythonpath: ${root_dir}/lib
requires:
'''
  # ./water/lib/water/__init__.py
  WATER__LIB__WATER____INIT___DOT_PY = '''\

'''
  # ./water/lib/water/common/__init__.py
  WATER__LIB__WATER__COMMON____INIT___DOT_PY = '''\
from .water_util import water_util
'''
  # ./water/lib/water/common/water_util.py
  WATER__LIB__WATER__COMMON__WATER_UTIL_DOT_PY = '''\
#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class water_util(object):
  
  @classmethod
  def water_func_one(clazz, x):
    return x

  @classmethod
  def water_func_two(clazz, x):
    return x

  @classmethod
  def water_util_a(clazz, x):
    return x

  @classmethod
  def water_util_b(clazz, x):
    return x
'''
# ./water/lib/__init__.py
  WATER__LIB____INIT___DOT_PY = '''\
'''
  # ./fiber/env/fiber.bescfg
  FIBER__ENV__FIBER_DOT_BESCFG = '''\
# fiber
name: fiber
unixpath: ${root_dir}/bin
pythonpath: ${root_dir}/lib
requires:
'''
  # ./orange/tests/lib/orange/common/test_orange_util.py
  ORANGE__TESTS__LIB__ORANGE__COMMON__TEST_ORANGE_UTIL_DOT_PY = '''\
#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

try:
  import pytest
  pytest.skip('does not work under pytest', allow_module_level = True)
except Exception as ex:
  pass
    
import unittest
from orange.common import orange_util

class test_orange_util(unittest.TestCase):

  def test_orange_func_one(self):
    self.assertEqual( 'a', orange_util.orange_func_one('a') )
  
  def test_orange_func_two(self):
    self.assertEqual( 'a', orange_util.orange_func_two('a') )
  
  def test_util_a_one(self):
    self.assertEqual( 'a', orange_util.util_a_one('a') )

  def test_util_b_one(self):
    self.assertEqual( 'a', orange_util.util_a_one('b') )

if __name__ == '__main__':
  unittest.main()
'''
  # ./orange/env/orange.bescfg
  ORANGE__ENV__ORANGE_DOT_BESCFG = '''\
# orange
name: orange
unixpath: ${root_dir}/bin
pythonpath: ${root_dir}/lib
requires: fruit citrus

'''
  # ./orange/lib/orange/common/orange_util.py
  ORANGE__LIB__ORANGE__COMMON__ORANGE_UTIL_DOT_PY = '''\
#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class orange_util(object):
  
  @classmethod
  def orange_func_one(clazz, x):
    return x

  @classmethod
  def orange_func_two(clazz, x):
    return x

  @classmethod
  def orange_util_a(clazz, x):
    return x

  @classmethod
  def orange_util_b(clazz, x):
    return x
'''
  # ./orange/lib/orange/common/__init__.py
  ORANGE__LIB__ORANGE__COMMON____INIT___DOT_PY = '''\
from .orange_util import orange_util
'''

  _ITEMS = [
    temp_content('file', 'citrus/env/citrus.bescfg', CITRUS__ENV__CITRUS_DOT_BESCFG, 0o0644),
    temp_content('file', 'fruit/env/fruit.bescfg', FRUIT__ENV__FRUIT_DOT_BESCFG, 0o0644),
    temp_content('file', 'kiwi/env/kiwi.bescfg', KIWI__ENV__KIWI_DOT_BESCFG, 0o0644),
    temp_content('file', 'water/env/water.bescfg', WATER__ENV__WATER_DOT_BESCFG, 0o0644),
    temp_content('file', 'water/lib/water/__init__.py', WATER__LIB__WATER____INIT___DOT_PY, 0o0644),
    temp_content('file', 'water/lib/water/common/__init__.py', WATER__LIB__WATER__COMMON____INIT___DOT_PY, 0o0644),
    temp_content('file', 'water/lib/water/common/water_util.py', WATER__LIB__WATER__COMMON__WATER_UTIL_DOT_PY, 0o0644),
    temp_content('file', 'water/lib/__init__.py', WATER__LIB____INIT___DOT_PY, 0o0644),
    temp_content('file', 'fiber/env/fiber.bescfg', FIBER__ENV__FIBER_DOT_BESCFG, 0o0644),
    temp_content('file', 'orange/tests/lib/orange/common/test_orange_util.py', ORANGE__TESTS__LIB__ORANGE__COMMON__TEST_ORANGE_UTIL_DOT_PY, 0o0644),
    temp_content('file', 'orange/env/orange.bescfg', ORANGE__ENV__ORANGE_DOT_BESCFG, 0o0644),
    temp_content('file', 'orange/lib/orange/common/orange_util.py', ORANGE__LIB__ORANGE__COMMON__ORANGE_UTIL_DOT_PY, 0o0644),
    temp_content('file', 'orange/lib/orange/common/__init__.py', ORANGE__LIB__ORANGE__COMMON____INIT___DOT_PY, 0o0644),
  ]
  
