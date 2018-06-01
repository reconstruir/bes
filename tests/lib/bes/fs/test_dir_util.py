#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path, unittest
from bes.fs import dir_util, file_util, temp_file

class test_dir_util(unittest.TestCase):

  def __make_tmp_files(self):
    tmp_dir = temp_file.make_temp_dir()
    file_util.save(path.join(tmp_dir, 'foo.txt'), content = 'foo.txt\n')
    file_util.save(path.join(tmp_dir, 'bar.txt'), content = 'bar.txt\n')
    file_util.save(path.join(tmp_dir, 'kiwi.jpg'), content = 'kiwi.jpg\n')
    file_util.save(path.join(tmp_dir, 'kiwi.png'), content = 'kiwi.png\n')
    file_util.save(path.join(tmp_dir, 'orange.png'), content = 'orange.png\n')
    return tmp_dir

  def test(self):
    tmp_dir = self.__make_tmp_files()
    expected_files = [
      'foo.txt',
      'bar.txt',
      'kiwi.jpg',
      'kiwi.png',
      'orange.png',
    ]
    expected_files = [ path.join(tmp_dir, f) for f in expected_files ]
    self.assertEqual( sorted(expected_files), dir_util.list(tmp_dir) )

  def test_list_relative(self):
    tmp_dir = self.__make_tmp_files()
    expected_files = [
      'foo.txt',
      'bar.txt',
      'kiwi.jpg',
      'kiwi.png',
      'orange.png',
    ]
    self.assertEqual( sorted(expected_files), dir_util.list(tmp_dir, relative = True) )

  def test_list_pattern(self):
    tmp_dir = self.__make_tmp_files()
    self.assertEqual( [ 'kiwi.jpg' ], dir_util.list(tmp_dir, relative = True, patterns = '*.jpg') )
    self.assertEqual( [ 'kiwi.jpg', 'kiwi.png' ], dir_util.list(tmp_dir, relative = True, patterns = 'kiwi*') )

  def test_all_parents(self):
    self.assertEqual( [ '/', '/usr', '/usr/lib' ], dir_util.all_parents('/usr/lib/foo' ) )

if __name__ == "__main__":
  unittest.main()
