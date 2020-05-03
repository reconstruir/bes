#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#
from bes.testing.unit_test import unit_test
from bes.system.env_override import env_override_temp_home_func

from bes.git.git_config import git_config

class test_git_config(unit_test):

  @env_override_temp_home_func()
  def test_get_never_set(self):
    self.assertEqual( None, git_config.get_value('user.name') )
    self.assertEqual( None, git_config.get_value('user.email') )

  @env_override_temp_home_func()
  def test_set_user_name_and_email(self):
    git_config.set_value('user.name', 'foo bar')
    self.assertEqual( 'foo bar', git_config.get_value('user.name') )
      
    git_config.set_value('user.email', 'foo@example.com')
    self.assertEqual( 'foo@example.com', git_config.get_value('user.email') )
    self.assertEqual( ( 'foo bar', 'foo@example.com' ), git_config.get_identity() )

  @env_override_temp_home_func()
  def test_set_identity(self):
    git_config.set_identity('green kiwi', 'kiwi@example.com')
    self.assertEqual( ( 'green kiwi', 'kiwi@example.com' ), git_config.get_identity() )

  @env_override_temp_home_func()
  def test_unset(self):
    git_config.set_identity('green kiwi', 'kiwi@example.com')
    git_config.unset_value('user.email')
    self.assertEqual( ( 'green kiwi', None ), git_config.get_identity() )

    git_config.unset_value('user.name')
    self.assertEqual( ( None, None ), git_config.get_identity() )
      
if __name__ == '__main__':
  unit_test.main()
