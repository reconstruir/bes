#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#

from bes.testing.unit_test import unit_test

from bes.git.git_commit_hash import git_commit_hash
from bes.git.git_error import git_error

class test_git_commit_hash(unit_test):

  def test_is_long(self):
    self.assertTrue( git_commit_hash.is_long('cd138635e1a94a6f2da6acbce3e2f2d584121d28') )
    self.assertFalse( git_commit_hash.is_long('zd138635e1a94a6f2da6acbce3e2f2d584121d28') )
    self.assertFalse( git_commit_hash.is_long('cd13863') )

  def test_is_short_hash(self):
    self.assertTrue( git_commit_hash.is_short('cd13863') )
    self.assertFalse( git_commit_hash.is_short('cd138635e1a94a6f2da6acbce3e2f2d584121d28') )
    self.assertFalse( git_commit_hash.is_short('zd13863') )
    
  def test_is_valid_char(self):
    self.assertTrue( git_commit_hash.is_valid_char('a') )
    self.assertFalse( git_commit_hash.is_valid_char('g') )

  def test_is_valid(self):
    self.assertTrue( git_commit_hash.is_valid('cd138635e1a94a6f2da6acbce3e2f2d584121d28') )
    self.assertFalse( git_commit_hash.is_valid('zd138635e1a94a6f2da6acbce3e2f2d584121d28') )
    self.assertTrue( git_commit_hash.is_valid('cd13863') )
    self.assertTrue( git_commit_hash.is_valid('cd138635e1a94a6f2da6acbce3e2f2d584121d28') )
    self.assertFalse( git_commit_hash.is_valid('zd13') )
    self.assertTrue( git_commit_hash.is_valid('cd13') )

  def test_check_is_short_success(self):
    git_commit_hash.check_is_short('cd13863')

  def test_check_is_short_failure(self):
    with self.assertRaises(git_error) as ctx:
      git_commit_hash.check_is_short('cd138635e1a94a6f2da6acbce3e2f2d584121d28')
      
  def test_check_is_long_success(self):
    git_commit_hash.check_is_long('cd138635e1a94a6f2da6acbce3e2f2d584121d28')

  def test_check_is_long_failure(self):
    with self.assertRaises(git_error) as ctx:
      git_commit_hash.check_is_long('cd13863')
      
if __name__ == '__main__':
  unit_test.main()
