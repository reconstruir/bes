#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#
from bes.testing.unit_test import unit_test
from bes.git.git_tag import git_tag
from bes.git.git_unit_test import git_temp_home_func

class test_git_tag(unit_test):

  @git_temp_home_func()
  def test_init(self):
    t = git_tag( '1.0.0', '18a911e5fd469294352004178190f49e59d936f9', '18a911e', False )
    self.assertEqual( '1.0.0', t.name )
    
if __name__ == '__main__':
  unit_test.main()
