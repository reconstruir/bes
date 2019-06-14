#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, tarfile
from bes.testing.unit_test import unit_test
from bes.fs.file_find import file_find
from bes.fs.file_copy import file_copy
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.fs.testing.temp_content import temp_content

class test_file_copy(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/bes.fs/tar_util'

  def test_copy_tree_basic(self):
    self.maxDiff = None
    src_tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    dst_tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    file_util.remove(dst_tmp_dir)
    with tarfile.open(self.data_path('test.tar'), mode = 'r') as f:
      f.extractall(path = src_tmp_dir)
    file_copy.copy_tree(src_tmp_dir, dst_tmp_dir)
    
    expected_files = [
      '1',
      '1/2',
      '1/2/3',
      '1/2/3/4',
      '1/2/3/4/5',
      '1/2/3/4/5/apple.txt',
      '1/2/3/4/5/kiwi.txt',
      'bar.txt',
      'empty',
      'foo.txt',
      'kiwi_link.txt',
    ]
    actual_files = file_find.find(dst_tmp_dir, file_type = file_find.ANY)
    self.assertEqual( expected_files, actual_files )
    
  def test_copy_tree_and_excludes(self):
    self.maxDiff = None
    src_tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    dst_tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    file_util.remove(dst_tmp_dir)
    with tarfile.open(self.data_path('test.tar'), mode = 'r') as f:
      f.extractall(path = src_tmp_dir)
      file_copy.copy_tree(src_tmp_dir, dst_tmp_dir, excludes = [ 'bar.txt', 'foo.txt' ])
    
    expected_files = [
      '1',
      '1/2',
      '1/2/3',
      '1/2/3/4',
      '1/2/3/4/5',
      '1/2/3/4/5/apple.txt',
      '1/2/3/4/5/kiwi.txt',
      'empty',
      'kiwi_link.txt',
    ]
    actual_files = file_find.find(dst_tmp_dir, file_type = file_find.ANY)
    self.assertEqual( expected_files, actual_files )

  def test_copy_tree_spaces_in_filenames(self):
    self.maxDiff = None
    src_tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG, suffix = '-has 2 spaces-')
    dst_tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG, suffix = '-has 2 spaces-')
    file_util.remove(dst_tmp_dir)
    with tarfile.open(self.data_path('test.tar'), mode = 'r') as f:
      f.extractall(path = src_tmp_dir)
    file_copy.copy_tree(src_tmp_dir, dst_tmp_dir)
    
    expected_files = [
      '1',
      '1/2',
      '1/2/3',
      '1/2/3/4',
      '1/2/3/4/5',
      '1/2/3/4/5/apple.txt',
      '1/2/3/4/5/kiwi.txt',
      'bar.txt',
      'empty',
      'foo.txt',
      'kiwi_link.txt',
    ]
    actual_files = file_find.find(dst_tmp_dir, file_type = file_find.ANY)
    self.assertEqual( expected_files, actual_files )

  def test_move_files(self):
    tmp_dir = temp_file.make_temp_dir()
    src_dir = path.join(tmp_dir, 'src')
    dst_dir = path.join(tmp_dir, 'dst')
    file_util.mkdir(dst_dir)
    temp_content.write_items([
      'file foo.txt "This is foo.txt\n" 644',
      'file bar.txt "This is bar.txt\n" 644',
      'file sub1/sub2/baz.txt "This is baz.txt\n" 644',
      'file yyy/zzz/vvv.txt "This is vvv.txt\n" 644',
      'file .hidden "this is .hidden\n" 644',
      'file script.sh "#!/bin/bash\necho script.sh\nexit 0\n" 755',
      'file .hushlogin "" 644',
    ], src_dir)
    expected = [
      '.hidden',
      '.hushlogin',
      'bar.txt',
      'foo.txt',
      'script.sh',
      'sub1/sub2/baz.txt',
      'yyy/zzz/vvv.txt',
    ]
    self.assertEqual( expected, file_find.find(src_dir, relative = True))
    file_copy.move_files(src_dir, dst_dir)
    self.assertEqual( expected, file_find.find(dst_dir, relative = True))
    self.assertEqual( [], file_find.find(src_dir, relative = True))
    
if __name__ == '__main__':
  unit_test.main()
