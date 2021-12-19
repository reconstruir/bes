#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.fs.file_find import file_find
from bes.fs.testing.temp_content import temp_content
from bes.refactor.refactor_files import refactor_files
from bes.testing.unit_test import unit_test

from _bes_unit_test_common.unit_test_media import unit_test_media
from _bes_unit_test_common.unit_test_media_files import unit_test_media_files

class test_refactor_files(unit_test, unit_test_media_files):

  @classmethod
  def _make_temp_content(clazz, items):
    return temp_content.write_items_to_temp_dir(items, delete = not clazz.DEBUG)

  def test_resolve_python_files(self):
    self.maxDiff = None
    tmp_dir = self._make_temp_content([
      temp_content('file', 'fruit/icons/kiwi.png', unit_test_media.PNG_SMALLEST_POSSIBLE, 0o0644),
      temp_content('file', 'fruit/icons/berry_wrong.py', unit_test_media.PNG_SMALLEST_POSSIBLE, 0o0644),
      temp_content('file', 'fruit/src/lemon.py', "class barolo(object): pass", 0o0644),
      temp_content('file', 'fruit/bin/fscript', "#!/usr/bin/env python3\na=666\n", 0o0755),
      temp_content('file', 'wine/icons/chablis.png', unit_test_media.PNG_SMALLEST_POSSIBLE, 0o0644),
      temp_content('file', 'wine/icons/sherry_wrong.py', unit_test_media.PNG_SMALLEST_POSSIBLE, 0o0644),
      temp_content('file', 'wine/src/barolo.py', "class barolo(object): pass", 0o0644),
      temp_content('file', 'wine/bin/wscript', "#!/usr/bin/env python3\na=666\n", 0o0755),
      temp_content('file', 'foo.py', "class foo(object): pass", 0o0644),
    ])
    [ path.join(tmp_dir, f) for f in [ 'fruit', 'wine', 'foo.py' ] ]
    self.assert_filename_list_equal( [
      f'{tmp_dir}/foo.py',
      f'{tmp_dir}/fruit/bin/fscript',
      f'{tmp_dir}/fruit/src/lemon.py',
      f'{tmp_dir}/wine/bin/wscript',
      f'{tmp_dir}/wine/src/barolo.py',
    ], refactor_files.resolve_python_files([ path.join(tmp_dir, f) for f in [ 'fruit', 'wine', 'foo.py' ] ]) )

  def test_search_files(self):
    self.maxDiff = None
    
    tmp_dir = self._make_temp_content([
      temp_content('file', 'lib/fruit/kiwi.py', self.KIWI_PY, 0o0644),
      temp_content('file', 'lib/fruit/lemon.py', self.LEMON_PY, 0o0644),
      temp_content('file', 'lib/fruit/constants.py', self.CONSTANTS_PY, 0o0644),
      temp_content('file', 'tests/lib/fruit/test_kiwi.py', self.TEST_KIWI_py, 0o0644),
      temp_content('file', 'tests/lib/fruit/test_lemon.py', self.TEST_LEMON_py, 0o0644),
    ])
    self.assert_filename_list_equal( [
      f'{tmp_dir}/lib/fruit/kiwi.py',
      f'{tmp_dir}/tests/lib/fruit/test_kiwi.py',
    ], refactor_files.search_files( file_find.find(tmp_dir, relative = False), 'kiwi', word_boundary = False, ignore_case = False) )

  def test_search_files_ignore_case(self):
    self.maxDiff = None
    
    tmp_dir = self._make_temp_content([
      temp_content('file', 'lib/fruit/kiwi.py', self.KIWI_PY, 0o0644),
      temp_content('file', 'lib/fruit/lemon.py', self.LEMON_PY, 0o0644),
      temp_content('file', 'lib/fruit/constants.py', self.CONSTANTS_PY, 0o0644),
      temp_content('file', 'tests/lib/fruit/test_kiwi.py', self.TEST_KIWI_py, 0o0644),
      temp_content('file', 'tests/lib/fruit/test_lemon.py', self.TEST_LEMON_py, 0o0644),
    ])
    self.assert_filename_list_equal( [
      f'{tmp_dir}/lib/fruit/constants.py',
      f'{tmp_dir}/lib/fruit/kiwi.py',
      f'{tmp_dir}/tests/lib/fruit/test_kiwi.py',
    ], refactor_files.search_files( file_find.find(tmp_dir, relative = False), 'kiwi', word_boundary = False, ignore_case = True) )

  KIWI_PY = '''\
class kiwi(object):
  def __init__(self, x):
    self._x = x

  @property
  def x(self):
    return self._x

  @classmethod
  def make_kiwi(clazz, x):
    return kiwi(x)
'''

  TEST_KIWI_py = '''\
from bes.testing.unit_test import unit_test
class test_kiwi(unit_test):

  def test__init__(self):
    self.assertEqual( 666, kiwi(666).x )

if __name__ == '__main__':
  unit_test.main()
'''

  LEMON_PY = '''\
class lemon(object):
  def __init__(self, x):
    self._x = x

  @property
  def x(self):
    return self._x

  @classmethod
  def make_lemon(clazz, x):
    return lemon(x)
'''

  TEST_LEMON_py = '''\
from bes.testing.unit_test import unit_test
class test_lemon(unit_test):

  def test__init__(self):
    self.assertEqual( 666, lemon(666).x )

if __name__ == '__main__':
  unit_test.main()
'''

  CONSTANTS_PY = '''\
_KIWI = 666
_KIWIFRUIT = 667
_LEMON = 668
_LEMONTHYME = 669
'''
    
if __name__ == '__main__':
  unit_test.main()
