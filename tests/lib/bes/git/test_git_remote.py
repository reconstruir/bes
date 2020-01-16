#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.git.git_remote import git_remote

class test_git_remote(unit_test):

  def test_parse_remote_url(self):
    f = git_remote.parse
    self.assertEqual( ( 'http', 'bitbucket.org', 'owner', 'project' ), f('http://bitbucket.org/owner/project') )
    self.assertEqual( ( 'ssh', 'bitbucket.org', 'owner', 'project' ), f('git@bitbucket.org:owner/project.git') )
    
if __name__ == '__main__':
  unit_test.main()
