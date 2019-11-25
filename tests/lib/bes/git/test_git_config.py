#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#
import os.path as path, os, unittest

from bes.testing.unit_test import unit_test
from bes.system.env_override import env_override_temp_home_func

from bes.git.git_config import git_config as G

class test_git_config(unit_test):

  @env_override_temp_home_func()
  def test_config(self):
    self.assertEqual( None, G.config_get_value('user.name') )
    self.assertEqual( None, G.config_get_value('user.email') )

    G.config_set_value('user.name', 'foo bar')
    self.assertEqual( 'foo bar', G.config_get_value('user.name') )
      
    G.config_set_value('user.email', 'foo@example.com')
    self.assertEqual( 'foo@example.com', G.config_get_value('user.email') )

    self.assertEqual( ( 'foo bar', 'foo@example.com' ), G.config_get_identity() )

    G.config_set_identity('green kiwi', 'kiwi@example.com')
    self.assertEqual( ( 'green kiwi', 'kiwi@example.com' ), G.config_get_identity() )

    G.config_unset_value('user.email')
    self.assertEqual( ( 'green kiwi', None ), G.config_get_identity() )

    G.config_unset_value('user.name')
    self.assertEqual( ( None, None ), G.config_get_identity() )
      
if __name__ == '__main__':
  unit_test.main()
