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

  def test_resolve_text_files(self):
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
      temp_content('file', 'README.MD', "this is README.MD", 0o0644),
      temp_content('file', 'data/foo.data', unit_test_media.UNKNOWN, 0o0644),
    ])
    [ path.join(tmp_dir, f) for f in [ 'fruit', 'wine', 'foo.py' ] ]
    self.assert_filename_list_equal( [
      f'{tmp_dir}/README.MD',
      f'{tmp_dir}/foo.py',
      f'{tmp_dir}/fruit/bin/fscript',
      f'{tmp_dir}/fruit/src/lemon.py',
      f'{tmp_dir}/wine/bin/wscript',
      f'{tmp_dir}/wine/src/barolo.py',
    ], refactor_files.resolve_text_files(tmp_dir) )
    
  def test_match_files(self):
    tmp_dir = self._make_temp_content([
      temp_content('file', 'lib/fruit/kiwi.py', self.KIWI_PY, 0o0644),
      temp_content('file', 'lib/fruit/lemon.py', self.LEMON_PY, 0o0644),
      temp_content('file', 'lib/fruit/constants.py', self.CONSTANTS_PY, 0o0644),
      temp_content('file', 'lib/fruit/constants2.py', self.CONSTANTS2_PY, 0o0644),
      temp_content('file', 'tests/lib/fruit/test_kiwi.py', self.TEST_KIWI_py, 0o0644),
      temp_content('file', 'tests/lib/fruit/test_lemon.py', self.TEST_LEMON_py, 0o0644),
    ])
    self.assert_filename_list_equal( [
      f'{tmp_dir}/lib/fruit/kiwi.py',
      f'{tmp_dir}/tests/lib/fruit/test_kiwi.py',
    ], refactor_files.match_files( file_find.find(tmp_dir, relative = False), 'kiwi', word_boundary = False) )

  def test_match_files_with_word_boundary(self):
    tmp_dir = self._make_temp_content([
      temp_content('file', 'lib/fruit/kiwi.py', self.KIWI_PY, 0o0644),
      temp_content('file', 'lib/fruit/lemon.py', self.LEMON_PY, 0o0644),
      temp_content('file', 'lib/fruit/constants.py', self.CONSTANTS_PY, 0o0644),
      temp_content('file', 'lib/fruit/constants2.py', self.CONSTANTS2_PY, 0o0644),
      temp_content('file', 'tests/lib/fruit/test_kiwi.py', self.TEST_KIWI_py, 0o0644),
      temp_content('file', 'tests/lib/fruit/test_lemon.py', self.TEST_LEMON_py, 0o0644),
    ])
    self.assert_filename_list_equal( [
      f'{tmp_dir}/lib/fruit/kiwi.py',
      f'{tmp_dir}/tests/lib/fruit/test_kiwi.py',
    ], refactor_files.match_files( file_find.find(tmp_dir, relative = False), 'kiwi', word_boundary = True) )

  def test_rename_dirs_one_file(self):
    tmp_dir = self._make_temp_content([
      temp_content('file', 'kiwi/xdata2/kiwi_stuff2/kiwi2.png', unit_test_media.PNG_SMALLEST_POSSIBLE, 0o0644),
    ])
    refactor_files.rename_dirs(tmp_dir, 'kiwi', 'chocolate', word_boundary = False)
    self.assert_filename_list_equal( [
      'chocolate',
      'chocolate/xdata2',
      'chocolate/xdata2/chocolate_stuff2',
      'chocolate/xdata2/chocolate_stuff2/kiwi2.png',
    ], file_find.find(tmp_dir, file_type = file_find.ANY) )

  def test_rename_dirs(self):
    tmp_dir = self._make_temp_content([
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
    refactor_files.rename_dirs(tmp_dir, 'kiwi', 'chocolate', word_boundary = False)
    self.assert_filename_list_equal( [
      'chocolate',
      'chocolate/xdata2',
      'chocolate/xdata2/chocolate_stuff2',
      'chocolate/xdata2/chocolate_stuff2/kiwi2.png',
      'empty_rootdir',
      'lib',
      'lib/fruit',
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
      'tests/lib/fruit/test_kiwi.py',
      'tests/lib/fruit/test_kiwi_fruit.py',
      'tests/lib/fruit/test_kiwifruit.py',
      'tests/lib/fruit/test_lemon.py',
      'tests/lib/fruity',
      'tests/lib/fruity/test_lemonb.py',
      'xdata',
      'xdata/chocolate_stuff',
      'xdata/chocolate_stuff/kiwi.png',                                     
    ], file_find.find(tmp_dir, file_type = file_find.ANY) )

  def test_rename_dirs_without_word_boundary(self):
    tmp_dir = self._make_temp_content([
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
    refactor_files.rename_dirs(tmp_dir, 'fruit', 'cheese', word_boundary = False)
    self.assert_filename_list_equal( [
      'empty_rootdir',
      'kiwi',
      'kiwi/xdata2',
      'kiwi/xdata2/kiwi_stuff2',
      'kiwi/xdata2/kiwi_stuff2/kiwi2.png',
      'lib',
      'lib/cheese',
      'lib/cheese/constants.py',
      'lib/cheese/constants2.py',
      'lib/cheese/emptydir',
      'lib/cheese/kiwi.py',
      'lib/cheese/kiwi_fruit.py',
      'lib/cheese/kiwifruit.py',
      'lib/cheese/lemon.py',
      'lib/cheesey',
      'lib/cheesey/constants2b.py',
      'tests',
      'tests/lib',
      'tests/lib/cheese',
      'tests/lib/cheese/test_kiwi.py',
      'tests/lib/cheese/test_kiwi_fruit.py',
      'tests/lib/cheese/test_kiwifruit.py',
      'tests/lib/cheese/test_lemon.py',
      'tests/lib/cheesey',
      'tests/lib/cheesey/test_lemonb.py',
      'xdata',
      'xdata/kiwi_stuff',
      'xdata/kiwi_stuff/kiwi.png',                                     
    ], file_find.find(tmp_dir, file_type = file_find.ANY) )

  def test_rename_dirs_with_word_boundary(self):
    tmp_dir = self._make_temp_content([
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
    refactor_files.rename_dirs(tmp_dir, 'fruit', 'cheese', word_boundary = True)
    self.assert_filename_list_equal( [
      'empty_rootdir',
      'kiwi',
      'kiwi/xdata2',
      'kiwi/xdata2/kiwi_stuff2',
      'kiwi/xdata2/kiwi_stuff2/kiwi2.png',
      'lib',
      'lib/cheese',
      'lib/cheese/constants.py',
      'lib/cheese/constants2.py',
      'lib/cheese/emptydir',
      'lib/cheese/kiwi.py',
      'lib/cheese/kiwi_fruit.py',
      'lib/cheese/kiwifruit.py',
      'lib/cheese/lemon.py',
      'lib/fruity',
      'lib/fruity/constants2b.py',
      'tests',
      'tests/lib',
      'tests/lib/cheese',
      'tests/lib/cheese/test_kiwi.py',
      'tests/lib/cheese/test_kiwi_fruit.py',
      'tests/lib/cheese/test_kiwifruit.py',
      'tests/lib/cheese/test_lemon.py',
      'tests/lib/fruity',
      'tests/lib/fruity/test_lemonb.py',
      'xdata',
      'xdata/kiwi_stuff',
      'xdata/kiwi_stuff/kiwi.png',                                     
    ], file_find.find(tmp_dir, file_type = file_find.ANY) )
    
  def test_rename_dirs_wont_leak_above_root_dir(self):
    'Test that we only rename dirs starting at root_dir'
    tmp_dir = self._make_temp_content([
      temp_content('file', 'fruit/fruit/lib/fruit/kiwi.py', self.KIWI_PY, 0o0644),
      temp_content('file', 'fruit/fruit/lib/fruit/lemon.py', self.LEMON_PY, 0o0644),
      temp_content('file', 'fruit/fruit/lib/fruit/constants.py', self.CONSTANTS_PY, 0o0644),
      temp_content('file', 'fruit/fruit/lib/fruit/constants2.py', self.CONSTANTS2_PY, 0o0644),
      temp_content('file', 'fruit/fruit/lib/fruity/constants2b.py', self.CONSTANTS2_PY, 0o0644),
      temp_content('file', 'fruit/fruit/tests/lib/fruit/test_kiwi.py', self.TEST_KIWI_py, 0o0644),
      temp_content('file', 'fruit/fruit/tests/lib/fruit/test_lemon.py', self.TEST_LEMON_py, 0o0644),
      temp_content('file', 'fruit/fruit/tests/lib/fruity/test_lemonb.py', self.TEST_LEMON_py, 0o0644),
    ])
    refactor_files.rename_dirs(path.join(tmp_dir, 'fruit'), 'fruit', 'cheese', word_boundary = False)
    self.assert_filename_list_equal( [
      'fruit',
      'fruit/cheese',
      'fruit/cheese/lib',
      'fruit/cheese/lib/cheese',
      'fruit/cheese/lib/cheese/constants.py',
      'fruit/cheese/lib/cheese/constants2.py',
      'fruit/cheese/lib/cheese/kiwi.py',
      'fruit/cheese/lib/cheese/lemon.py',
      'fruit/cheese/lib/cheesey',
      'fruit/cheese/lib/cheesey/constants2b.py',      
      'fruit/cheese/tests',
      'fruit/cheese/tests/lib',
      'fruit/cheese/tests/lib/cheese',
      'fruit/cheese/tests/lib/cheese/test_kiwi.py',
      'fruit/cheese/tests/lib/cheese/test_lemon.py',
      'fruit/cheese/tests/lib/cheesey',
      'fruit/cheese/tests/lib/cheesey/test_lemonb.py',
    ], file_find.find(tmp_dir, file_type = file_find.ANY) )

  def test_rename_files(self):
    tmp_dir = self._make_temp_content([
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
    refactor_files.rename_files(tmp_dir, 'kiwi', 'chocolate', word_boundary = False)
    self.assert_filename_list_equal( [
      'chocolate',
      'chocolate/xdata2',
      'chocolate/xdata2/chocolate_stuff2',
      'chocolate/xdata2/chocolate_stuff2/chocolate2.png',
      'empty_rootdir',
      'lib',
      'lib/fruit',
      'lib/fruit/chocolate.py',
      'lib/fruit/chocolate_fruit.py',
      'lib/fruit/chocolatefruit.py',
      'lib/fruit/constants.py',
      'lib/fruit/constants2.py',
      'lib/fruit/emptydir',
      'lib/fruit/lemon.py',
      'lib/fruity',
      'lib/fruity/constants2b.py',
      'tests',
      'tests/lib',
      'tests/lib/fruit',
      'tests/lib/fruit/test_chocolate.py',
      'tests/lib/fruit/test_chocolate_fruit.py',
      'tests/lib/fruit/test_chocolatefruit.py',
      'tests/lib/fruit/test_lemon.py',
      'tests/lib/fruity',
      'tests/lib/fruity/test_lemonb.py',
      'xdata',
      'xdata/chocolate_stuff',
      'xdata/chocolate_stuff/chocolate.png',
    ], file_find.find(tmp_dir, file_type = file_find.ANY) )

  def test_rename_files_with_word_boundary(self):
    tmp_dir = self._make_temp_content([
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
    refactor_files.rename_files(tmp_dir, 'kiwi', 'chocolate', word_boundary = True)
    self.assert_filename_list_equal( [
      'chocolate',
      'chocolate/xdata2',
      'chocolate/xdata2/kiwi_stuff2',
      'chocolate/xdata2/kiwi_stuff2/kiwi2.png',
      'empty_rootdir',
      'lib',
      'lib/fruit',
      'lib/fruit/chocolate.py',
      'lib/fruit/constants.py',
      'lib/fruit/constants2.py',
      'lib/fruit/emptydir',
      'lib/fruit/kiwi_fruit.py',
      'lib/fruit/kiwifruit.py',
      'lib/fruit/lemon.py',
      'lib/fruity',
      'lib/fruity/constants2b.py',
      'tests',
      'tests/lib',
      'tests/lib/fruit',
      'tests/lib/fruit/test_kiwi.py',
      'tests/lib/fruit/test_kiwi_fruit.py',
      'tests/lib/fruit/test_kiwifruit.py',
      'tests/lib/fruit/test_lemon.py',
      'tests/lib/fruity',
      'tests/lib/fruity/test_lemonb.py',
      'xdata',
      'xdata/kiwi_stuff',
      'xdata/kiwi_stuff/chocolate.png',
    ], file_find.find(tmp_dir, file_type = file_find.ANY) )

  def test_rename_files_with_word_boundary_and_underscore(self):
    tmp_dir = self._make_temp_content([
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
    refactor_files.rename_files(tmp_dir, 'kiwi', 'chocolate', word_boundary = True, underscore = True)
    self.assert_filename_list_equal( [
      'chocolate',
      'chocolate/xdata2',
      'chocolate/xdata2/chocolate_stuff2',
      'chocolate/xdata2/chocolate_stuff2/kiwi2.png',
      'empty_rootdir',
      'lib',
      'lib/fruit',
      'lib/fruit/chocolate.py',
      'lib/fruit/chocolate_fruit.py',
      'lib/fruit/constants.py',
      'lib/fruit/constants2.py',
      'lib/fruit/emptydir',
      'lib/fruit/kiwifruit.py',
      'lib/fruit/lemon.py',
      'lib/fruity',
      'lib/fruity/constants2b.py',
      'tests',
      'tests/lib',
      'tests/lib/fruit',
      'tests/lib/fruit/test_chocolate.py',
      'tests/lib/fruit/test_chocolate_fruit.py',
      'tests/lib/fruit/test_kiwifruit.py',
      'tests/lib/fruit/test_lemon.py',
      'tests/lib/fruity',
      'tests/lib/fruity/test_lemonb.py',
      'xdata',
      'xdata/chocolate_stuff',
      'xdata/chocolate_stuff/chocolate.png',
    ], file_find.find(tmp_dir, file_type = file_find.ANY) )

  def test_rename_dirs_caca(self):
    tmp_dir = self._make_temp_content([
      temp_content('file', 'kiwi/xdata2/kiwi_stuff2/kiwi2.png', unit_test_media.PNG_SMALLEST_POSSIBLE, 0o0644),
    ])
    refactor_files.rename_dirs(tmp_dir, 'kiwi', 'kiwifruit', word_boundary = False)
    self.assert_filename_list_equal( [
      'kiwifruit',
      'kiwifruit/xdata2',
      'kiwifruit/xdata2/kiwifruit_stuff2',
      'kiwifruit/xdata2/kiwifruit_stuff2/kiwi2.png',
    ], file_find.find(tmp_dir, file_type = file_find.ANY) )
    
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
