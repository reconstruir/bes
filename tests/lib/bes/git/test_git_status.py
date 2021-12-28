#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.git.git_status import git_status

class test_status(unit_test):

  def test___eq__(self):
    self.assertEqual( ( 'R', 'foo.py' ), git_status('R', 'foo.py') )

  def test_as_tuple(self):
    self.assertEqual( ( 'R', 'foo.py' ), git_status('R', 'foo.py').as_tuple() )
  
  def test_parse_line(self):
    self.assertEqual( ( 'A', 'foo.py' ), git_status.parse_line('A  foo.py') )

if __name__ == '__main__':
  unit_test.main()
