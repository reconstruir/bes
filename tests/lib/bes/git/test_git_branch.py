#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#
import unittest

from bes.git.git_branch import git_branch as GB
from bes.git.git_unit_test import git_temp_home_func

class test_git_branch(unittest.TestCase):

  @git_temp_home_func()
  def test_parse_branch_status(self):
    self.assertEqual( ( 1, 1 ), GB.parse_branch_status('[ahead 1, behind 1]') )
    self.assertEqual( ( 1, 0 ), GB.parse_branch_status('[ahead 1]') )
    self.assertEqual( ( 0, 1 ), GB.parse_branch_status('[behind 1]') )
    self.assertEqual( ( 0, 0 ), GB.parse_branch_status('[]') )
    self.assertEqual( ( 0, 0 ), GB.parse_branch_status('') )
    self.assertEqual( ( 1, 1 ), GB.parse_branch_status('[ahead 1, behind 1] this is foo') )
    self.assertEqual( ( 1, 0 ), GB.parse_branch_status('[ahead 1] this is foo') )
    self.assertEqual( ( 0, 1 ), GB.parse_branch_status('[behind 1] this is foo') )
    self.assertEqual( ( 1, 1 ), GB.parse_branch_status('[ahead 1, behind 1]this is foo') )
    self.assertEqual( ( 1, 0 ), GB.parse_branch_status('[ahead 1]this is foo') )
    self.assertEqual( ( 0, 1 ), GB.parse_branch_status('[behind 1]this is foo') )
    
  @git_temp_home_func()
  def test_strip_branch_status(self):
    self.assertEqual( '', GB.strip_branch_status('[ahead 1, behind 1]') )
    self.assertEqual( '', GB.strip_branch_status('[ahead 1]') )
    self.assertEqual( '', GB.strip_branch_status('[behind 1]') )
    self.assertEqual( '[]', GB.strip_branch_status('[]') )
    self.assertEqual( '', GB.strip_branch_status('') )
    self.assertEqual( ' this is foo', GB.strip_branch_status('[ahead 1, behind 1] this is foo') )
    self.assertEqual( ' this is foo', GB.strip_branch_status('[ahead 1] this is foo') )
    self.assertEqual( ' this is foo', GB.strip_branch_status('[behind 1] this is foo') )
    self.assertEqual( 'this is foo', GB.strip_branch_status('[ahead 1, behind 1]this is foo') )
    self.assertEqual( 'this is foo', GB.strip_branch_status('[ahead 1]this is foo') )
    self.assertEqual( 'this is foo', GB.strip_branch_status('[behind 1]this is foo') )
    
if __name__ == "__main__":
  unittest.main()
