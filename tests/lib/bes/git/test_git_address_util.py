#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#
import os.path as path

from bes.testing.unit_test import unit_test
from bes.git.git_unit_test import git_temp_home_func
from bes.fs.file_util import file_util

from bes.git.git import git
from bes.git.git_address_util import git_address_util
from bes.git.git_temp_repo import git_temp_repo

class test_git_address_util(unit_test):

  @git_temp_home_func()
  def test_name(self):
    self.assertEqual( 'bar', git_address_util.name('https://foohub.com/myproj/bar.git') )
    self.assertEqual( 'foo-bar-baz', git_address_util.name('git@git:foo-bar-baz.git') )
    r = git_temp_repo(debug = self.DEBUG)
    self.assertEqual( path.basename(r.root), git_address_util.name(r.root) )
  
  @git_temp_home_func()
  def test_resolve(self):
    self.assertEqual( 'https://github.com/git/git.git', git_address_util.resolve('https://github.com/git/git.git') )
    self.assertEqual( 'git@github.com/git/git.git', git_address_util.resolve('git@github.com/git/git.git') )
    tmp_repo = path.expanduser('~/minerepo')
    file_util.mkdir(tmp_repo)
    git.init(tmp_repo)
    self.assertEqual( tmp_repo, git_address_util.resolve('~/minerepo') )

  @git_temp_home_func()
  def test_sanitize_for_local_path(self):
    self.assertEqual( 'https___github.com_git_git.git', git_address_util.sanitize_for_local_path('https://github.com/git/git.git') )
    
if __name__ == '__main__':
  unit_test.main()
