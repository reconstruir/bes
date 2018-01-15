#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from bes.testing.unit_test import unit_test
from bes.fs import file_replace, file_util, temp_file
import os.path as path

class test_file_replace(unit_test):

  __unit_test_data_dir__ = '../../../../test_data/bes.fs/file_replace'

  def test_file_replace_ascii(self):
    tmp_file = self._make_temp_replace_file('ascii.txt')
    replacements = {
      'This': 'That',
      'foo': 'bar',
    }
    file_replace.replace(tmp_file, replacements, backup = False, word_boundary = True)
    self.assertEqual('That is bar.\n', file_util.read(tmp_file, codec = 'utf-8'))
    
  def test_file_replace_utf8(self):
    tmp_file = self._make_temp_replace_file('utf8.txt')
    replacements = {
      'This': 'That',
    }
    file_replace.replace(tmp_file, replacements, backup = False, word_boundary = True)
    self.assertEqual(u'That is bér.\n', file_util.read(tmp_file, codec = 'utf-8'))
    
  def _make_temp_replace_file(self, filename):
    src_file = self.data_path(filename)
    tmp_dir = temp_file.make_temp_dir()
    tmp_file = path.join(tmp_dir, path.basename(src_file))
    file_util.copy(src_file, tmp_file)
    return tmp_file
    
if __name__ == '__main__':
  unit_test.main()
