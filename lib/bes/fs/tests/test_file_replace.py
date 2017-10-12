#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from bes.testing.unit_test import unit_test
from bes.fs import file_replace, file_util, temp_file
import os.path as path

class test_file_replace(unit_test):

  __unit_test_data_dir__ = 'test_data/file_replace'

  def test_file_replace(self):
    src_file = self.data_path('foo.txt')
    tmp_dir = temp_file.make_temp_dir()
    tmp_file = path.join(tmp_dir, 'foo.txt')
    file_util.copy(src_file, tmp_file)
    replacements = {
      'This': 'That',
      'foo': 'bar',
    }
    file_replace.replace(tmp_file, replacements, backup = False, word_boundary = True)
    self.assertEqual('This is foo.\n', file_util.read(src_file, codec = 'utf-8'))
    self.assertEqual('That is bar.\n', file_util.read(tmp_file, codec = 'utf-8'))
    
if __name__ == '__main__':
  unit_test.main()
