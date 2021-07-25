#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys
import os.path as path

from bes.fs.file_util import file_util
from bes.git.git_error import git_error
from bes.git.git_repo import git_repo
from bes.git.git_temp_repo import git_temp_repo
from bes.git.git_unit_test import git_temp_home_func
from bes.git.git_status_getter import git_status_getter
from bes.system.env_override import env_override_temp_home_func
from bes.testing.unit_test import unit_test
from bes.git.git_repo_status_options import git_repo_status_options

class test_git_status_getter(unit_test):

  @git_temp_home_func()
  def test_repo_status(self):

    NUM_REPOS = 9
    NUM_THREADS = 3

    options = git_repo_status_options(num_threads = NUM_THREADS)
    
    repos = []

    repo_index_map = {}
    
    for i in range(0, NUM_REPOS):
      config = '''\
add commit1 commit1
  kiwi{index}.txt: this is kiwi{index}.txt
add commit2 commit2
  lemon{index}.txt: this is lemon{index}.txt
'''.format(index = i)
      r = git_temp_repo(remote = True, debug = self.DEBUG, config = config, prefix = 'status')
      repos.append(r.repo)
      repo_index_map[r.repo] = i
        
    result = git_status_getter.get_repo_status(repos, options = options)
    for repo, status in result.items():
      index = repo_index_map[repo]
      self.assertEqual( 'master', status.active_branch )
      self.assertEqual( repo.last_commit_hash(), status.last_commit.commit_hash_long )
      self.assertEqual( 'add lemon{index}.txt'.format(index = index), status.last_commit.message )
      self.assertEqual( 'unittest', status.last_commit.author )
      self.assertEqual( 'unittest@example.com', status.last_commit.email )
      self.assertEqual( False, status.last_commit.is_merge_commit )
      self.assertEqual( ( 0, 0 ), status.branch_status )
    
if __name__ == '__main__':
  unit_test.main()
