#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.git import git_util

class test_git_util(unit_test):

  def test_name_from_address(self):
    self.assertEqual( 'bar', git_util.name_from_address('https://foohub.com/myproj/bar.git') )
    self.assertEqual( 'foo-bar-baz', git_util.name_from_address('git@git:foo-bar-baz.git') )
  
if __name__ == '__main__':
  unit_test.main()
