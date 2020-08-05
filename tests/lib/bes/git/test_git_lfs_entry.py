#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.git.git_lfs_entry import git_lfs_entry

class test_git_lfs_entry(unit_test):

  def test_parse(self):
    f = git_lfs_entry.parse_entry
    self.assertEqual( ( 'foo.txt', 'abcdef01234567890abcdef01234567890abcdef01234567890abcdef0123456', True ), 
                      f('abcdef01234567890abcdef01234567890abcdef01234567890abcdef0123456 - foo.txt') )
    
if __name__ == '__main__':
  unit_test.main()
