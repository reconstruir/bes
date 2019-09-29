#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.git.git_status import git_status as S

class test_status(unit_test):

  def test_as_tuple(self):
    self.assertEqual( ( 'R', 'foo.py', 'bar.py' ), S('R', 'foo.py', 'bar.py').as_tuple() )
  
  def test___eq__(self):
    self.assertEqual( ( 'R', 'foo.py', 'bar.py' ), S('R', 'foo.py', 'bar.py') )

  def test_parse_line(self):
    self.assertEqual( S( 'A', 'foo.py' ), S.parse_line('A  foo.py') )

if __name__ == '__main__':
  unit_test.main()
