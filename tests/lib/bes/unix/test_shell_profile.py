#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.unix.shell_profile import shell_profile as SP

class test_shell_profile(unit_test):

  def test_shell_is_bash(self):
    print( SP.shell_is_bash() )
    
if __name__ == '__main__':
  unit_test.main()
