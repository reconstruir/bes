#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.unix.shell.shell import shell
from bes.system.user import user
from bes.testing.unit_test_skip import raise_skip_if_not_unix

class test_shell(unit_test):

  @classmethod
  def setUpClass(clazz):
    raise_skip_if_not_unix()
  
  def test_valid_shells(self):
    v = shell.valid_shells()
    self.assertTrue( '/bin/bash' in v )
    self.assertTrue( '/bin/sh' in v )

  def test_has_shell(self):
    self.assertTrue( shell.has_shell('/bin/bash') )
    self.assertTrue( shell.has_shell('/bin/sh') )

  def test_shell_for_user(self):
    s = shell.shell_for_user(username = user.USERNAME)
    self.assertTrue( s in shell.valid_shells() )
    
if __name__ == '__main__':
  unit_test.main()
