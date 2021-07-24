#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys
import os.path as path

from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.git.git import git
from bes.git.git_error import git_error
from bes.git.git_repo import git_repo
from bes.git.git_status import git_status
from bes.git.git_temp_repo import git_temp_repo
from bes.git.git_unit_test import git_temp_home_func
from bes.git.git_multi_repo_status import git_multi_repo_status
from bes.system.env_override import env_override_temp_home_func
from bes.system.execute import execute
from bes.testing.unit_test import unit_test

class test_git_multi_repo_status(unit_test):

  @git_temp_home_func()
  def test_repo_status(self):
    self.maxDiff = -1
    config = '''\
add commit1 commit1
  kiwi.txt: this is kiwi.txt
add commit2 commit2
  lemon.txt: this is lemon.txt
'''
    r = git_temp_repo(remote = True, debug = self.DEBUG, config = config, prefix = 'status')
    result = git_multi_repo_status.status([ r.repo ]) #, options = None):
    st = result[r.repo]
    self.assertEqual( 'master', st.active_branch )
    self.assertEqual( r.last_commit_hash(), st.last_commit.commit_hash_long )
    self.assertEqual( 'add lemon.txt', st.last_commit.message )
    self.assertEqual( 'unittest', st.last_commit.author )
    self.assertEqual( 'unittest@example.com', st.last_commit.email )
    self.assertEqual( False, st.last_commit.is_merge_commit )
    self.assertEqual( ( 0, 0 ), st.branch_status )
    
if __name__ == '__main__':
  unit_test.main()
