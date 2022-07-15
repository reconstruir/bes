#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.git.git_status import git_status
from bes.git.git_status_action import git_status_action

class test_status(unit_test):

  def test___eq__(self):
    self.assertEqual( ( git_status_action.RENAMED, 'foo.py', None ),
                      git_status(git_status_action.RENAMED, 'foo.py', None) )

  def test_as_tuple(self):
    self.assertEqual( ( git_status_action.RENAMED, 'foo.py', None ),
                      git_status(git_status_action.RENAMED, 'foo.py', None).as_tuple() )
  
  def test_parse_line(self):
    self.assertEqual( ( git_status_action.ADDED, 'foo.py', None ),
                      git_status.parse_line('A  foo.py') )
    
  def test_parse_line_with_rename(self):
    self.assertEqual( ( git_status_action.RENAMED, 'foo.py', 'bar.py' ),
                      git_status.parse_line('R  foo.py -> bar.py') )

if __name__ == '__main__':
  unit_test.main()
