#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs.filename_list import filename_list

class test_filename_list(unit_test):

  def test_prefixes(self):
    self.assertEqual( { 'kiwi', 'lemon', 'sour-cherry', 'SOUR-CHERRY' }, filename_list.prefixes([
      '.DS_Store',
      'kiwi-100.txt',
      'kiwi-101.txt',
      'lemon-100.txt',
      'lemon-101.txt',
      'lemon-100.txt',
      'lemonade.txt',
      'sour-cherry-1.txt',
      'sour-cherry-2.txt',
      'SOUR-CHERRY-1.txt',
      'SOUR-CHERRY-2.txt',
    ]) )
    
  def test_prefixes_with_ignore_case(self):
    self.assertEqual( { 'kiwi', 'sour-cherry' }, filename_list.prefixes([
      'sour-cherry-1.txt',
      'sour-cherry-2.txt',
      'SOUR-CHERRY-1.txt',
      'SOUR-CHERRY-2.txt',
      'kiwi-100.txt',
      'kiwi-101.txt',
    ], ignore_case = True) )

  def test_startswith(self):
    self.assertEqual( True, filename_list.startswith([ 'kiwi/foo.txt', 'kiwi/bar.txt' ], 'kiwi/') )
    self.assertEqual( False, filename_list.startswith([ 'kiwi/foo.txt', 'kiwi/bar.txt' ], 'apple/') )
    self.assertEqual( False, filename_list.startswith([ 'kiwi/foo.txt', 'apple/bar.txt' ], 'apple/') )
    
if __name__ == '__main__':
  unit_test.main()
