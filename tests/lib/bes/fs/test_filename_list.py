#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs.filename_list import filename_list

class test_filename_list(unit_test):

  def test_prefixes(self):
    self.assertEqual( { 'kiwi', 'lemon', 'sour-cherry' }, filename_list.prefixes([
      '.DS_Store',
      'kiwi-100.txt',
      'kiwi-101.txt',
      'lemon-100.txt',
      'lemon-101.txt',
      'lemon-100.txt',
      'lemonade.txt',
      'sour-cherry-1.txt',
      'sour-cherry-2.txt',
    ]) )
    
if __name__ == '__main__':
  unit_test.main()
