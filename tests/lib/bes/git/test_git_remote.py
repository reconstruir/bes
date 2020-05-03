#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.git.git_remote import git_remote
from bes.git.git_temp_repo import git_temp_repo
from bes.git.git_unit_test import git_temp_home_func
from bes.testing.unit_test import unit_test

class test_git_remote(unit_test):

  def test_parse_remote_url_bitbucket_http(self):
    self.assertEqual( ( 'http', 'bitbucket.org', 'owner', 'project' ), git_remote.parse('http://bitbucket.org/owner/project') )
    self.assertEqual( ( 'ssh', 'bitbucket.org', 'owner', 'project' ), git_remote.parse('git@bitbucket.org:owner/project.git') )
    
  def test_parse_remote_url_bitbucket_ssh(self):
    self.assertEqual( ( 'ssh', 'bitbucket.org', 'owner', 'project' ), git_remote.parse('git@bitbucket.org:owner/project.git') )
    
  @git_temp_home_func()
  def test_parse_local(self):
    items = [
      'file foo.txt "foo.txt"',
    ]
    r = git_temp_repo(remote = True, content = items, debug = self.DEBUG, prefix = '.repo')
    self.assertEqual( ( 'local', None, None, r.root ), git_remote.parse(r.root) )
    
  @git_temp_home_func()
  def test_parse_local_bare(self):
    items = [
      'file foo.txt "foo.txt"',
    ]
    r = git_temp_repo(remote = True, content = items, debug = self.DEBUG, prefix = '.repo')
    self.assertEqual( ( 'bare_local', None, None, r.address ), git_remote.parse(r.address) )
    
  @git_temp_home_func()
  def xtest_parse_local_non_existent(self):
    self.assertEqual( ( 'ssh', 'bitbucket.org', 'owner', 'project' ), git_remote.parse('git@bitbucket.org:owner/project.git') )
    
if __name__ == '__main__':
  unit_test.main()
