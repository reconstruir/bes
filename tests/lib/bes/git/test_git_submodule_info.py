#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.git.git_submodule_info import git_submodule_info as SI

class test_git_submodule_info(unit_test):

  def test_parse_not_current(self):
    self.assertEqual( ( 'sub1', '1234567890abcdef1234567890abcdef12345678', False, None ),
                      SI.parse('-1234567890abcdef1234567890abcdef12345678 sub1') )

  def test_parse_current(self):
    self.assertEqual( ( 'sub1', '1234567890abcdef1234567890abcdef12345678', True, None ),
                      SI.parse(' 1234567890abcdef1234567890abcdef12345678 sub1') )

  def test_parse_not_current_with_tag(self):
    self.assertEqual( ( 'sub1', '1234567890abcdef1234567890abcdef12345678', False, 'tag666' ),
                      SI.parse('-1234567890abcdef1234567890abcdef12345678 sub1 (tag666)') )

  def test_parse_current_with_tag(self):
    self.assertEqual( ( 'sub1', '1234567890abcdef1234567890abcdef12345678', True, 'tag666' ),
                      SI.parse(' 1234567890abcdef1234567890abcdef12345678 sub1 (tag666)') )

if __name__ == '__main__':
  unit_test.main()
