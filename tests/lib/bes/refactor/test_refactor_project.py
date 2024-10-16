#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.fs.file_find import file_find
from bes.fs.testing.temp_content import temp_content
from bes.git.git_repo import git_repo
from bes.git.git_temp_repo import git_temp_repo
from bes.git.git_unit_test import git_temp_home_func
from bes.refactor.refactor_options import refactor_options
from bes.refactor.refactor_project import refactor_project
from bes.testing.unit_test import unit_test
from bes.text.word_boundary import word_boundary

from _bes_unit_test_common.unit_test_media import unit_test_media
from _bes_unit_test_common.unit_test_media_files import unit_test_media_files

class test_refactor_project(unit_test, unit_test_media_files):

  @classmethod
  def _make_temp_content(clazz, items):
    r = git_temp_repo(remote = True, debug = clazz.DEBUG)
    temp_content.write_items(items, r.root)
    r.add('.')
    r.commit('add', '.')
    return r

  @git_temp_home_func()
  def test_rename(self):
    r = self._make_temp_content([
      temp_content('dir', 'empty_rootdir', None, 0o0755),
      temp_content('dir', 'lib/fruit/emptydir', None, 0o0755),
      temp_content('file', 'lib/fruit/constants.py', self.CONSTANTS_PY, 0o0644),
      temp_content('file', 'lib/fruit/constants2.py', self.CONSTANTS2_PY, 0o0644),
      temp_content('file', 'lib/fruit/kiwi.py', self.KIWI_PY, 0o0644),
      temp_content('file', 'lib/fruit/kiwifruit.py', self.KIWI_PY, 0o0644),
      temp_content('file', 'lib/fruit/kiwi_fruit.py', self.KIWI_PY, 0o0644),
      temp_content('file', 'lib/fruit/lemon.py', self.LEMON_PY, 0o0644),
      temp_content('file', 'lib/fruity/constants2b.py', self.CONSTANTS2_PY, 0o0644),
      temp_content('file', 'tests/lib/fruit/test_kiwi.py', self.TEST_KIWI_py, 0o0644),
      temp_content('file', 'tests/lib/fruit/test_kiwifruit.py', self.TEST_KIWI_py, 0o0644),
      temp_content('file', 'tests/lib/fruit/test_kiwi_fruit.py', self.TEST_KIWI_py, 0o0644),
      temp_content('file', 'tests/lib/fruit/test_lemon.py', self.TEST_LEMON_py, 0o0644),
      temp_content('file', 'tests/lib/fruity/test_lemonb.py', self.TEST_LEMON_py, 0o0644),
      temp_content('file', 'xdata/kiwi_stuff/kiwi.png', unit_test_media.PNG_SMALLEST_POSSIBLE, 0o0644),
      temp_content('file', 'kiwi/xdata2/kiwi_stuff2/kiwi2.png', unit_test_media.PNG_SMALLEST_POSSIBLE, 0o0644),
    ])
    args = [
      f'{r.root}/lib',
      f'{r.root}/tests',
      f'{r.root}/xdata',
      f'{r.root}/kiwi',
    ]
    options = refactor_options(try_git = True,
                               word_boundary = False)
    refactor_project.rename(args, 'fruit', 'cheese', options = options)
    self.assert_string_equal_fuzzy( '''\
R lib/fruit/constants.py -> lib/cheese/constants.py
R lib/fruit/constants2.py -> lib/cheese/constants2.py
R lib/fruit/kiwi.py -> lib/cheese/kiwi.py
R lib/fruit/kiwi_fruit.py -> lib/cheese/kiwi_cheese.py
R lib/fruit/kiwifruit.py -> lib/cheese/kiwicheese.py
R lib/fruit/lemon.py -> lib/cheese/lemon.py
R lib/fruity/constants2b.py -> lib/cheesey/constants2b.py
R tests/lib/fruit/test_kiwi.py -> tests/lib/cheese/test_kiwi.py
R tests/lib/fruit/test_kiwi_fruit.py -> tests/lib/cheese/test_kiwi_cheese.py
R tests/lib/fruit/test_kiwifruit.py -> tests/lib/cheese/test_kiwicheese.py
R tests/lib/fruit/test_lemon.py -> tests/lib/cheese/test_lemon.py
R tests/lib/fruity/test_lemonb.py -> tests/lib/cheesey/test_lemonb.py
''', r.status_as_string('.') )
    self.assert_string_equal_fuzzy( '''\
empty_rootdir
kiwi
kiwi/xdata2
kiwi/xdata2/kiwi_stuff2
kiwi/xdata2/kiwi_stuff2/kiwi2.png
lib
lib/cheese
lib/cheese/constants.py
lib/cheese/constants2.py
lib/cheese/kiwi.py
lib/cheese/kiwi_cheese.py
lib/cheese/kiwicheese.py
lib/cheese/lemon.py
lib/cheesey
lib/cheesey/constants2b.py
lib/fruit
lib/fruit/emptydir
tests
tests/lib
tests/lib/cheese
tests/lib/cheese/test_kiwi.py
tests/lib/cheese/test_kiwi_cheese.py
tests/lib/cheese/test_kiwicheese.py
tests/lib/cheese/test_lemon.py
tests/lib/cheesey
tests/lib/cheesey/test_lemonb.py
xdata
xdata/kiwi_stuff
xdata/kiwi_stuff/kiwi.png
''', r.find_all_files_as_string(file_type = file_find.ANY) )

  @git_temp_home_func()
  def test_rename_with_gitignore(self):
    r = self._make_temp_content([
      temp_content('dir', 'empty_rootdir', None, 0o0755),
      temp_content('dir', 'lib/fruit/emptydir', None, 0o0755),
      temp_content('file', '.gitignore', '*~\n', 0o0644),
      temp_content('file', 'lib/fruit/constants.py', self.CONSTANTS_PY, 0o0644),
      temp_content('file', 'lib/fruit/constants2.py', self.CONSTANTS2_PY, 0o0644),
      temp_content('file', 'lib/fruit/kiwi.py', self.KIWI_PY, 0o0644),
      temp_content('file', 'lib/fruit/kiwifruit.py', self.KIWI_PY, 0o0644),
      temp_content('file', 'lib/fruit/kiwi_fruit.py', self.KIWI_PY, 0o0644),
      temp_content('file', 'lib/fruit/lemon.py', self.LEMON_PY, 0o0644),
      temp_content('file', 'lib/fruity/constants2b.py', self.CONSTANTS2_PY, 0o0644),
      temp_content('file', 'tests/lib/fruit/test_kiwi.py', self.TEST_KIWI_py, 0o0644),
      temp_content('file', 'tests/lib/fruit/test_kiwifruit.py', self.TEST_KIWI_py, 0o0644),
      temp_content('file', 'tests/lib/fruit/test_kiwifruit.py~', self.TEST_KIWI_py, 0o0644),
      temp_content('file', 'tests/lib/fruit/test_kiwi_fruit.py', self.TEST_KIWI_py, 0o0644),
      temp_content('file', 'tests/lib/fruit/test_lemon.py', self.TEST_LEMON_py, 0o0644),
      temp_content('file', 'tests/lib/fruity/test_lemonb.py', self.TEST_LEMON_py, 0o0644),
      temp_content('file', 'xdata/kiwi_stuff/kiwi.png', unit_test_media.PNG_SMALLEST_POSSIBLE, 0o0644),
      temp_content('file', 'kiwi/xdata2/kiwi_stuff2/kiwi2.png', unit_test_media.PNG_SMALLEST_POSSIBLE, 0o0644),
    ])
    args = [
      f'{r.root}/lib',
      f'{r.root}/tests',
      f'{r.root}/xdata',
      f'{r.root}/kiwi',
    ]
    options = refactor_options(try_git = True,
                               word_boundary = False)
    refactor_project.rename(args, 'fruit', 'cheese', options = options)
    self.assert_string_equal_fuzzy( '''\
R lib/fruit/constants.py -> lib/cheese/constants.py
R lib/fruit/constants2.py -> lib/cheese/constants2.py
R lib/fruit/kiwi.py -> lib/cheese/kiwi.py
R lib/fruit/kiwi_fruit.py -> lib/cheese/kiwi_cheese.py
R lib/fruit/kiwifruit.py -> lib/cheese/kiwicheese.py
R lib/fruit/lemon.py -> lib/cheese/lemon.py
R lib/fruity/constants2b.py -> lib/cheesey/constants2b.py
R tests/lib/fruit/test_kiwi.py -> tests/lib/cheese/test_kiwi.py
R tests/lib/fruit/test_kiwi_fruit.py -> tests/lib/cheese/test_kiwi_cheese.py
R tests/lib/fruit/test_kiwifruit.py -> tests/lib/cheese/test_kiwicheese.py
R tests/lib/fruit/test_lemon.py -> tests/lib/cheese/test_lemon.py
R tests/lib/fruity/test_lemonb.py -> tests/lib/cheesey/test_lemonb.py
''', r.status_as_string('.') )
    self.assert_string_equal_fuzzy( '''\
.gitignore
empty_rootdir
kiwi
kiwi/xdata2
kiwi/xdata2/kiwi_stuff2
kiwi/xdata2/kiwi_stuff2/kiwi2.png
lib
lib/cheese
lib/cheese/constants.py
lib/cheese/constants2.py
lib/cheese/kiwi.py
lib/cheese/kiwi_cheese.py
lib/cheese/kiwicheese.py
lib/cheese/lemon.py
lib/cheesey
lib/cheesey/constants2b.py
lib/fruit
lib/fruit/emptydir
tests
tests/lib
tests/lib/cheese
tests/lib/cheese/test_kiwi.py
tests/lib/cheese/test_kiwi_cheese.py
tests/lib/cheese/test_kiwicheese.py
tests/lib/cheese/test_kiwicheese.py~
tests/lib/cheese/test_lemon.py
tests/lib/cheesey
tests/lib/cheesey/test_lemonb.py
xdata
xdata/kiwi_stuff
xdata/kiwi_stuff/kiwi.png
''', r.find_all_files_as_string(file_type = file_find.ANY) )
    
  @git_temp_home_func()
  def test_copy(self):
    r = self._make_temp_content([
      temp_content('dir', 'empty_rootdir', None, 0o0755),
      temp_content('dir', 'lib/fruit/emptydir', None, 0o0755),
      temp_content('file', 'lib/fruit/constants.py', self.CONSTANTS_PY, 0o0644),
      temp_content('file', 'lib/fruit/constants2.py', self.CONSTANTS2_PY, 0o0644),
      temp_content('file', 'lib/fruit/kiwi.py', self.KIWI_PY, 0o0644),
      temp_content('file', 'lib/fruit/kiwifruit.py', self.KIWI_PY, 0o0644),
      temp_content('file', 'lib/fruit/kiwi_fruit.py', self.KIWI_PY, 0o0644),
      temp_content('file', 'lib/fruit/lemon.py', self.LEMON_PY, 0o0644),
      temp_content('file', 'lib/fruity/constants2b.py', self.CONSTANTS2_PY, 0o0644),
      temp_content('file', 'tests/lib/fruit/test_kiwi.py', self.TEST_KIWI_py, 0o0644),
      temp_content('file', 'tests/lib/fruit/test_kiwifruit.py', self.TEST_KIWI_py, 0o0644),
      temp_content('file', 'tests/lib/fruit/test_kiwi_fruit.py', self.TEST_KIWI_py, 0o0644),
      temp_content('file', 'tests/lib/fruit/test_lemon.py', self.TEST_LEMON_py, 0o0644),
      temp_content('file', 'tests/lib/fruity/test_lemonb.py', self.TEST_LEMON_py, 0o0644),
      temp_content('file', 'xdata/kiwi_stuff/kiwi.png', unit_test_media.PNG_SMALLEST_POSSIBLE, 0o0644),
      temp_content('file', 'kiwi/xdata2/kiwi_stuff2/kiwi2.png', unit_test_media.PNG_SMALLEST_POSSIBLE, 0o0644),
    ])
    args = [
      f'{r.root}/lib',
      f'{r.root}/tests',
      f'{r.root}/xdata',
      f'{r.root}/kiwi',
    ]
    options = refactor_options(try_git = True,
                               word_boundary = False)
    refactor_project.copy(args, 'kiwi', 'cheese', False, options = options)
    self.assertEqual( [
      ( 'A', 'kiwi/xdata2/kiwi_stuff2/cheese2.png', None ),
      ( 'AM', 'lib/fruit/cheese.py', None ),
      ( 'AM', 'lib/fruit/cheese_fruit.py', None ),
      ( 'AM', 'lib/fruit/cheesefruit.py', None ),
      ( 'AM', 'tests/lib/fruit/test_cheese.py', None ),
      ( 'AM', 'tests/lib/fruit/test_cheese_fruit.py', None ),
      ( 'AM', 'tests/lib/fruit/test_cheesefruit.py', None ),
      ( 'A', 'xdata/kiwi_stuff/cheese.png', None ),
    ], r.status('.') )
    self.assert_filename_list_equal( [
      'empty_rootdir',
      'kiwi',
      'kiwi/xdata2',
      'kiwi/xdata2/kiwi_stuff2',
      'kiwi/xdata2/kiwi_stuff2/cheese2.png',
      'kiwi/xdata2/kiwi_stuff2/kiwi2.png',
      'lib',
      'lib/fruit',
      'lib/fruit/cheese.py',
      'lib/fruit/cheese_fruit.py',
      'lib/fruit/cheesefruit.py',
      'lib/fruit/constants.py',
      'lib/fruit/constants2.py',
      'lib/fruit/emptydir',
      'lib/fruit/kiwi.py',
      'lib/fruit/kiwi_fruit.py',
      'lib/fruit/kiwifruit.py',
      'lib/fruit/lemon.py',
      'lib/fruity',
      'lib/fruity/constants2b.py',
      'tests',
      'tests/lib',
      'tests/lib/fruit',
      'tests/lib/fruit/test_cheese.py',
      'tests/lib/fruit/test_cheese_fruit.py',
      'tests/lib/fruit/test_cheesefruit.py',
      'tests/lib/fruit/test_kiwi.py',
      'tests/lib/fruit/test_kiwi_fruit.py',
      'tests/lib/fruit/test_kiwifruit.py',
      'tests/lib/fruit/test_lemon.py',
      'tests/lib/fruity',
      'tests/lib/fruity/test_lemonb.py',
      'xdata',
      'xdata/kiwi_stuff',
      'xdata/kiwi_stuff/cheese.png',
      'xdata/kiwi_stuff/kiwi.png',
    ], r.find_all_files(file_type = file_find.ANY) )

    self.assert_text_file_equal_fuzzy(self.KIWI_PY, r.file_path('lib/fruit/kiwi.py') )
    self.assert_text_file_equal_fuzzy('''\
class cheese(object):
  def __init__(self, x):
    self._x = x

  @property
  def x(self):
    return self._x

  @classmethod
  def make_cheese(clazz, x):
    return cheese(x)
''', r.file_path('lib/fruit/cheese.py') )
    
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
KIWI = 666
LEMON = 668
'''

  CONSTANTS2_PY = '''\
KIWIFRUIT = 667
LEMONTHYME = 669
'''
  
if __name__ == '__main__':
  unit_test.main()
