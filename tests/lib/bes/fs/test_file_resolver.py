#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
# todo:
#  - symlink unit tests
from bes.fs.file_resolver import file_resolver
from bes.fs.file_resolver_item import file_resolver_item
from bes.fs.file_resolver_options import file_resolver_options
from bes.fs.file_sort_order import file_sort_order
from bes.fs.testing.temp_content import temp_content
from bes.testing.unit_test import unit_test

class test_file_resolve(unit_test):

  def test_resolve_files_just_root_dir(self):
    expected = '''\
    ${tmp_dir} cheese.txt ${tmp_dir}/cheese.txt 0 0
    '''
    actual = self._test_resolve_files([
      'file cheese.txt "this is cheese.txt" 644',
      'file a/lemon.txt "this is lemon.txt" 644',
      'file b/kiwi.txt "this is kiwi.txt" 644',
      'file subdir/orange.txt "this is orange.txt" 644',
      'file subdir/apple.txt "this is apple.txt" 644',
    ], [ '${tmp_dir}' ], recursive = False)
    self.assert_string_equal( expected, actual, ignore_white_space = True, multi_line = True )

  def test_resolve_files_just_root_dir_recursive(self):
    expected = '''\
    ${tmp_dir} a/lemon.txt ${tmp_dir}/a/lemon.txt 0 0
    ${tmp_dir} b/kiwi.txt ${tmp_dir}/b/kiwi.txt 1 1
    ${tmp_dir} cheese.txt ${tmp_dir}/cheese.txt 2 2
    ${tmp_dir} subdir/apple.txt ${tmp_dir}/subdir/apple.txt 3 3
    ${tmp_dir} subdir/orange.txt ${tmp_dir}/subdir/orange.txt 4 4
    '''
    actual = self._test_resolve_files([
      'file cheese.txt "this is cheese.txt" 644',
      'file a/lemon.txt "this is lemon.txt" 644',
      'file b/kiwi.txt "this is kiwi.txt" 644',
      'file subdir/orange.txt "this is orange.txt" 644',
      'file subdir/apple.txt "this is apple.txt" 644',
    ], [ '${tmp_dir}' ], recursive = True)
    self.assert_string_equal( expected, actual, ignore_white_space = True, multi_line = True )

  def test_resolve_files_two_dirs(self):
    expected = '''\
    ${tmp_dir}/a lemon.txt ${tmp_dir}/a/lemon.txt 0 0
    ${tmp_dir}/b kiwi.txt ${tmp_dir}/b/kiwi.txt 1 1
    '''
    actual = self._test_resolve_files([
      'file cheese.txt "this is cheese.txt" 644',
      'file a/lemon.txt "this is lemon.txt" 644',
      'file b/kiwi.txt "this is kiwi.txt" 644',
      'file subdir/orange.txt "this is orange.txt" 644',
      'file subdir/apple.txt "this is apple.txt" 644',
    ], [ '${tmp_dir}/a', '${tmp_dir}/b' ], recursive = False)
    self.assert_string_equal( expected, actual, ignore_white_space = True, multi_line = True )

  def test_resolve_files_two_dirs_recursive(self):
    expected = '''\
    ${tmp_dir}/a suba1/orange.txt      ${tmp_dir}/a/suba1/orange.txt      0 0
    ${tmp_dir}/a suba1/suba2/lemon.txt ${tmp_dir}/a/suba1/suba2/lemon.txt 1 1
    ${tmp_dir}/a watermelon.txt        ${tmp_dir}/a/watermelon.txt        2 2
    ${tmp_dir}/b pineapple.txt         ${tmp_dir}/b/pineapple.txt         3 3
    ${tmp_dir}/b subb1/cherry.txt      ${tmp_dir}/b/subb1/cherry.txt      4 4
    ${tmp_dir}/b subb1/subb2/kiwi.txt  ${tmp_dir}/b/subb1/subb2/kiwi.txt  5 5
    '''
    actual = self._test_resolve_files([
      'file a/suba1/orange.txt "this is orange.txt" 644',
      'file a/suba1/suba2/lemon.txt "this is lemon.txt" 644',
      'file a/watermelon.txt "this is watermelon.txt" 644',
      'file b/pineapple.txt "this is pineapple.txt" 644',
      'file b/subb1/cherry.txt "this is cherry.txt" 644',
      'file b/subb1/subb2/kiwi.txt "this is kiwi.txt" 644',
    ], [ '${tmp_dir}/a', '${tmp_dir}/b' ], recursive = True)
    self.assert_string_equal( expected, actual, ignore_white_space = True, multi_line = True )

  def test_resolve_files_with_limit(self):
    expected = '''\
    ${tmp_dir}/a suba1/orange.txt      ${tmp_dir}/a/suba1/orange.txt      0 0
    '''
    actual = self._test_resolve_files([
      'file a/suba1/orange.txt "this is orange.txt" 644',
      'file a/suba1/suba2/lemon.txt "this is lemon.txt" 644',
      'file a/watermelon.txt "this is watermelon.txt" 644',
      'file b/pineapple.txt "this is pineapple.txt" 644',
      'file b/subb1/cherry.txt "this is cherry.txt" 644',
      'file b/subb1/subb2/kiwi.txt "this is kiwi.txt" 644',
    ], [ '${tmp_dir}/a', '${tmp_dir}/b' ], recursive = True, limit = 1)
    self.assert_string_equal( expected, actual, ignore_white_space = True, multi_line = True )

  def test_resolve_files_with_sort_order(self):
    expected = '''\
    ${tmp_dir}/b subb1/cherry.txt      ${tmp_dir}/b/subb1/cherry.txt      0 4
    ${tmp_dir}/b pineapple.txt         ${tmp_dir}/b/pineapple.txt         1 3
    ${tmp_dir}/b subb1/subb2/kiwi.txt  ${tmp_dir}/b/subb1/subb2/kiwi.txt  2 5
    ${tmp_dir}/a suba1/suba2/lemon.txt ${tmp_dir}/a/suba1/suba2/lemon.txt 3 1
    ${tmp_dir}/a suba1/orange.txt      ${tmp_dir}/a/suba1/orange.txt      4 0
    ${tmp_dir}/a watermelon.txt        ${tmp_dir}/a/watermelon.txt        5 2
    '''
    actual = self._test_resolve_files([
      'file b/subb1/cherry.txt "1" 644',         # 1 byte
      'file b/pineapple.txt "12" 644',           # 2 bytes
      'file b/subb1/subb2/kiwi.txt "123" 644',   # 3 bytes
      'file a/suba1/suba2/lemon.txt "1234" 644', # 4 bytes
      'file a/suba1/orange.txt "12345" 644',     # 5 bytes
      'file a/watermelon.txt "123456" 644',      # 6 bytes
    ], [ '${tmp_dir}/a', '${tmp_dir}/b' ], recursive = True, sort_order = 'size')
    self.assert_string_equal( expected, actual, ignore_white_space = True, multi_line = True )

  def test_resolve_files_with_sort_order_reverse(self):
    expected = '''\
    ${tmp_dir}/a watermelon.txt        ${tmp_dir}/a/watermelon.txt        0 2
    ${tmp_dir}/a suba1/orange.txt      ${tmp_dir}/a/suba1/orange.txt      1 0
    ${tmp_dir}/a suba1/suba2/lemon.txt ${tmp_dir}/a/suba1/suba2/lemon.txt 2 1
    ${tmp_dir}/b subb1/subb2/kiwi.txt  ${tmp_dir}/b/subb1/subb2/kiwi.txt  3 5
    ${tmp_dir}/b pineapple.txt         ${tmp_dir}/b/pineapple.txt         4 3
    ${tmp_dir}/b subb1/cherry.txt      ${tmp_dir}/b/subb1/cherry.txt      5 4
    '''
    actual = self._test_resolve_files([
      'file b/subb1/cherry.txt "1" 644',         # 1 byte
      'file b/pineapple.txt "12" 644',           # 2 bytes
      'file b/subb1/subb2/kiwi.txt "123" 644',   # 3 bytes
      'file a/suba1/suba2/lemon.txt "1234" 644', # 4 bytes
      'file a/suba1/orange.txt "12345" 644',     # 5 bytes
      'file a/watermelon.txt "123456" 644',      # 6 bytes
    ], [ '${tmp_dir}/a', '${tmp_dir}/b' ], recursive = True, sort_order = 'size', sort_reverse = True)
    self.assert_string_equal( expected, actual, ignore_white_space = True, multi_line = True )

  def test_resolve_files_with_one_pattern(self):
    expected = '''\
    ${tmp_dir}/a suba1/suba2/two.lemon ${tmp_dir}/a/suba1/suba2/two.lemon 0 0
    ${tmp_dir}/b subb1/five.lemon ${tmp_dir}/b/subb1/five.lemon 1 1
'''
    actual = self._test_resolve_files([
      'file a/suba1/one.orange "this is one.orange" 644',
      'file a/suba1/suba2/two.lemon "this is two.lemon" 644',
      'file a/three.orange "this is three.orange" 644',
      'file b/four.pineapple "this is four.pineapple" 644',
      'file b/subb1/five.lemon "this is five.lemon" 644',
      'file b/subb1/subb2/six.kiwi "this is six.kiwi" 644',
    ], [ '${tmp_dir}/a', '${tmp_dir}/b' ], recursive = True, match_patterns = [ '*.lemon' ])
    self.assert_string_equal( expected, actual, ignore_white_space = True, multi_line = True )

  def test_resolve_files_with_many_patterns(self):
    expected = '''\
    ${tmp_dir}/a suba1/suba2/two.lemon ${tmp_dir}/a/suba1/suba2/two.lemon 0 0
    ${tmp_dir}/a three.orange ${tmp_dir}/a/three.orange 1 1
    ${tmp_dir}/b subb1/five.lemon ${tmp_dir}/b/subb1/five.lemon 2 2
    ${tmp_dir}/b subb1/subb2/six.kiwi ${tmp_dir}/b/subb1/subb2/six.kiwi 3 3
'''
    actual = self._test_resolve_files([
      'file a/suba1/one.orange "this is one.orange" 644',
      'file a/suba1/suba2/two.lemon "this is two.lemon" 644',
      'file a/three.orange "this is three.orange" 644',
      'file b/four.pineapple "this is four.pineapple" 644',
      'file b/subb1/five.lemon "this is five.lemon" 644',
      'file b/subb1/subb2/six.kiwi "this is six.kiwi" 644',
      'file b/subb1/subb2/seven.orange "this is seven.orange" 644',
    ], [ '${tmp_dir}/a', '${tmp_dir}/b' ], recursive = True, match_patterns = [ '*.lemon', 'three.orange', '*.kiwi' ])
    self.assert_string_equal( expected, actual, ignore_white_space = True, multi_line = True )

  def test_resolve_dirs_just_root_dir(self):
    expected = '''\
    ${tmp_dir} a ${tmp_dir}/a 0 0
    ${tmp_dir} b ${tmp_dir}/b 1 1
    ${tmp_dir} subdir1 ${tmp_dir}/subdir1 2 2
    ${tmp_dir} subdir2 ${tmp_dir}/subdir2 3 3
    '''
    actual = self._test_resolve_dirs([
      'file cheese.txt "this is cheese.txt" 644',
      'file a/lemon.txt "this is lemon.txt" 644',
      'file b/kiwi.txt "this is kiwi.txt" 644',
      'file subdir1/subdir3/orange.txt "this is orange.txt" 644',
      'file subdir2/subdir4/apple.txt "this is apple.txt" 644',
    ], [ '${tmp_dir}' ], recursive = False)
    self.assert_string_equal( expected, actual, ignore_white_space = True, multi_line = True )

  def test_resolve_dirs_just_root_dir_recursive(self):
    expected = '''\
    ${tmp_dir} a ${tmp_dir}/a 0 0
    ${tmp_dir} b ${tmp_dir}/b 1 1
    ${tmp_dir} subdir1 ${tmp_dir}/subdir1 2 2
    ${tmp_dir} subdir1/subdir3 ${tmp_dir}/subdir1/subdir3 3 3
    ${tmp_dir} subdir2 ${tmp_dir}/subdir2 4 4
    ${tmp_dir} subdir2/subdir4 ${tmp_dir}/subdir2/subdir4 5 5
    '''
    actual = self._test_resolve_dirs([
      'file cheese.txt "this is cheese.txt" 644',
      'file a/lemon.txt "this is lemon.txt" 644',
      'file b/kiwi.txt "this is kiwi.txt" 644',
      'file subdir1/subdir3/orange.txt "this is orange.txt" 644',
      'file subdir2/subdir4/apple.txt "this is apple.txt" 644',
    ], [ '${tmp_dir}' ], recursive = True)
    self.assert_string_equal( expected, actual, ignore_white_space = True, multi_line = True )

  def test_resolve_dirs_just_root_dir_recursive_sort_order_depth(self):
    expected = '''\
    ${tmp_dir} a ${tmp_dir}/a 0 0
    ${tmp_dir} b ${tmp_dir}/b 1 1
    ${tmp_dir} subdir1 ${tmp_dir}/subdir1 2 2
    ${tmp_dir} subdir2 ${tmp_dir}/subdir2 3 4
    ${tmp_dir} subdir1/subdir3 ${tmp_dir}/subdir1/subdir3 4 3
    ${tmp_dir} subdir2/subdir4 ${tmp_dir}/subdir2/subdir4 5 5
    '''
    actual = self._test_resolve_dirs([
      'file cheese.txt "this is cheese.txt" 644',
      'file a/lemon.txt "this is lemon.txt" 644',
      'file b/kiwi.txt "this is kiwi.txt" 644',
      'file subdir1/subdir3/orange.txt "this is orange.txt" 644',
      'file subdir2/subdir4/apple.txt "this is apple.txt" 644',
    ], [ '${tmp_dir}' ], recursive = True, sort_order = 'depth')
    self.assert_string_equal( expected, actual, ignore_white_space = True, multi_line = True )

  def test_resolve_files_one_file(self):
    expected = '''\
    ${tmp_dir} subdir/apple.txt ${tmp_dir}/subdir/apple.txt 0 0
    '''
    actual = self._test_resolve_files([
      'file subdir/apple.txt "this is apple.txt" 644',
    ], [ '${tmp_dir}' ], recursive = True)
    self.assert_string_equal( expected, actual, ignore_white_space = True, multi_line = True )

  def test_resolve_files_two_files_same_subdir(self):
    expected = '''\
    ${tmp_dir}/subdir apple.txt ${tmp_dir}/subdir/apple.txt 0 0
    ${tmp_dir}/subdir kiwi.txt ${tmp_dir}/subdir/kiwi.txt 1 1
    '''
    actual = self._test_resolve_files([
      'file subdir/apple.txt "this is apple.txt" 644',
      'file subdir/kiwi.txt "this is kiwi.txt" 644',
    ], [ '${tmp_dir}/subdir' ], recursive = True)
    self.assert_string_equal( expected, actual, ignore_white_space = True, multi_line = True )

  def test_resolve_files_two_files_root_and_subdir(self):
    expected = '''\
    ${tmp_dir} apple.txt ${tmp_dir}/apple.txt 0 0
    ${tmp_dir} subdir/kiwi.txt ${tmp_dir}/subdir/kiwi.txt 1 1
    '''
    actual = self._test_resolve_files([
      'file apple.txt "this is apple.txt" 644',
      'file subdir/kiwi.txt "this is kiwi.txt" 644',
    ], [ '${tmp_dir}' ], recursive = True)
    self.assert_string_equal( expected, actual, ignore_white_space = True, multi_line = True )

  def test_resolve_files_with_ignore_files(self):
    tmp_ignore_content1 = '''
.config
'''
    tmp_ignore_file1 = self.make_temp_file(content = tmp_ignore_content1)
    tmp_ignore_content2 = '''
*.foo
'''
    tmp_ignore_file2 = self.make_temp_file(content = tmp_ignore_content2)
    expected = '''\
    ${tmp_dir} a/lemon.txt ${tmp_dir}/a/lemon.txt 0 0
    ${tmp_dir} b/kiwi.txt ${tmp_dir}/b/kiwi.txt 1 1
    ${tmp_dir} cheese.txt ${tmp_dir}/cheese.txt 2 2
    ${tmp_dir} subdir/apple.txt ${tmp_dir}/subdir/apple.txt 3 3
    ${tmp_dir} subdir/orange.txt ${tmp_dir}/subdir/orange.txt 4 4
    '''
    actual = self._test_resolve_files([
      'file .config "this is .config" 644',
      'file cheese.txt "this is cheese.txt" 644',
      'file a/.config "this is a/.config" 644',
      'file a/lemon.txt "this is lemon.txt" 644',
      'file b/.config "this is b/.config" 644',
      'file b/kiwi.txt "this is kiwi.txt" 644',
      'file b/cotton.foo "this is cotton.foo" 644',
      'file b/leather.foo "this is leather.foo" 644',
      'file subdir/.config "this is subdir/.config" 644',
      'file subdir/gasoline.foo "this is gasoline.foo" 644',
      'file subdir/orange.txt "this is orange.txt" 644',
      'file subdir/apple.txt "this is apple.txt" 644',
    ], [ '${tmp_dir}' ], recursive = True, ignore_files = [ tmp_ignore_file1, tmp_ignore_file2 ] )
    self.assert_string_equal( expected, actual, ignore_white_space = True, multi_line = True )
    
  def _test_resolve_files(self,
                          items,
                          files,
                          recursive = True,
                          limit = None,
                          sort_order = None,
                          sort_reverse = False,
                          match_patterns = None,
                          match_type = None,
                          match_basename = True,
                          match_function = None,
                          match_re = None,
                          ignore_files = None):
    return self._test_resolve(file_resolver.resolve_files,
                              items,
                              files,
                              recursive = recursive,
                              limit = limit,
                              sort_order = sort_order,
                              sort_reverse = sort_reverse,
                              match_patterns = match_patterns,
                              match_type = match_type,
                              match_basename = match_basename,
                              match_function = match_function,
                              match_re = match_re,
                              ignore_files = ignore_files)

  def _test_resolve_dirs(self,
                         items,
                         files,
                         recursive = True,
                         limit = None,
                         sort_order = None,
                         sort_reverse = False,
                         match_patterns = None,
                         match_type = None,
                         match_basename = True,
                         match_function = None,
                         match_re = None):
    return self._test_resolve(file_resolver.resolve_dirs,
                              items,
                              files,
                              recursive = recursive,
                              limit = limit,
                              sort_order = sort_order,
                              sort_reverse = sort_reverse,
                              match_patterns = match_patterns,
                              match_type = match_type,
                              match_basename = match_basename,
                              match_function = match_function,
                              match_re = match_re,
                              ignore_files = None)
  
  def _test_resolve(self,
                    func,
                    items,
                    files,
                    recursive = True,
                    limit = None,
                    sort_order = None,
                    sort_reverse = False,
                    match_patterns = None,
                    match_type = None,
                    match_basename = True,
                    match_function = None,
                    match_re = None,
                    ignore_files = None):
    tmp_dir = self.make_temp_dir()
    temp_content.write_items(items, tmp_dir)
    files = [ f.replace('${tmp_dir}', tmp_dir) for f in files ]
    options = file_resolver_options(recursive = recursive,
                                    limit = limit,
                                    sort_order = sort_order,
                                    sort_reverse = sort_reverse,
                                    match_patterns = match_patterns,
                                    match_type = match_type,
                                    match_basename = match_basename,
                                    match_function = match_function,
                                    match_re = match_re,
                                    ignore_files = ignore_files)
    result = func(files, options = options)
    return os.linesep.join([ self._fix_one_resolved_file(f, tmp_dir) for f in result ])
  
  @classmethod
  def _fix_one_resolved_file(clazz, resolved_file, tmp_dir):
    if resolved_file.root_dir != None:
      new_root_dir = resolved_file.root_dir.replace(tmp_dir, '${tmp_dir}')
      new_root_dir = clazz.xp_filename(new_root_dir)
      
    else:
      new_root_dir = None
    new_filename_abs = resolved_file.filename_abs.replace(tmp_dir, '${tmp_dir}')
    item = file_resolver_item(new_root_dir,
                              clazz.xp_filename(resolved_file.filename),
                              clazz.xp_filename(new_filename_abs),
                              resolved_file.index,
                              resolved_file.found_index)
    return ' '.join([ str(part) for part in item ])
  
  def _make_temp_content(self):
    tmp_dir = self.make_temp_dir()
    items = [
      'file cheese/soft/brie.cheese "this is brie" 644',
      'file cheese/hard/cheddar.cheese "this is cheddar" 644',
      'file fruit/kiwi.fruit "this is kiwi" 644',
      'file fruit/orange.fruit "this is orange" 644',
    ]
    temp_content.write_items(items, tmp_dir)
    return tmp_dir

  def test_resolve_files_two_files_deep(self):
    expected = '''\
    ${tmp_dir}/fruit fruit/tests/lib/fruit/test_kiwi.py ${tmp_dir}/fruit/fruit/tests/lib/fruit/test_kiwi.py 0 0
    ${tmp_dir}/fruit fruit/tests/lib/fruit/test_lemon.py ${tmp_dir}/fruit/fruit/tests/lib/fruit/test_lemon.py 1 1
    '''
    actual = self._test_resolve_files([
      'file fruit/fruit/tests/lib/fruit/test_lemon.py "this is test lemon" 644',
      'file fruit/fruit/tests/lib/fruit/test_kiwi.py "this is test kiwi" 644',
    ], [ '${tmp_dir}/fruit' ], recursive = True)
    self.assert_string_equal( expected, actual, ignore_white_space = True, multi_line = True )
  
if __name__ == "__main__":
  unit_test.main()
