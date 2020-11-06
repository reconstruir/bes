#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import multiprocessing

from bes.testing.unit_test import unit_test

from bes.git.git_repo_operation_options import git_repo_operation_options
from bes.git.git_temp_repo import git_temp_repo
from bes.git.git_unit_test import git_temp_home_func
from bes.git.git_util import git_util

class test_git_util_repo_update_submodule(unit_test):

  @git_temp_home_func()
  def test_simple(self):
    sub_content = [
      'file subfoo.txt "this is subfoo" 644',
    ]
    sub_repo = self._make_repo(remote = True, content = sub_content, prefix = '-mod-')
    rev1 = sub_repo.last_commit_hash(short_hash = True)
    
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r1 = self._make_repo(remote = True, content = content, prefix = '-main-')
    self.assertEqual( [ 'foo.txt' ], r1.find_all_files() )

    r1.submodule_add(sub_repo.address, 'submod1')
    r1.commit('add mod submodule', '.')
    r1.push()

    self.assertEqual( rev1, r1.submodule_status_one('submod1').revision )
    
    rev2 = sub_repo.add_file('sub_kiwi.txt', 'this is sub_kiwi.txt', push = True)

    self.assertEqual( rev1, r1.submodule_status_one('submod1').revision )

    git_util.repo_update_submodule(r1.address, 'submod1', 'master', rev2, False)

    r1.pull()

    r1.submodule_init(submodule = 'submod1')
    
    self.assertEqual( rev2, r1.submodule_status_one('submod1').revision )
    
  @git_temp_home_func()
  def test_two_submodules(self):
    sub_content1 = [
      'file subfoo1.txt "this is subrepo1" 644',
    ]
    sub_repo1 = self._make_repo(remote = True, content = sub_content1, prefix = '-subrepo1-')
    sub_repo1_rev1 = sub_repo1.last_commit_hash(short_hash = True)

    sub_content2 = [
      'file subfoo2.txt "this is subrepo2" 644',
    ]
    sub_repo2 = self._make_repo(remote = True, content = sub_content2, prefix = '-subprepo2-')
    sub_repo2_rev1 = sub_repo2.last_commit_hash(short_hash = True)
    
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r1 = self._make_repo(remote = True, content = content, prefix = '-main-')
    self.assertEqual( [ 'foo.txt' ], r1.find_all_files() )

    r1.submodule_add(sub_repo1.address, 'submod1')
    r1.commit('add mod submod1', [ '.gitmodules', 'submod1' ])
    r1.push()

    self.assertEqual( sub_repo1_rev1, r1.submodule_status_one('submod1').revision )
    
    r1.submodule_add(sub_repo2.address, 'submod2')
    r1.commit('add mod submod2', [ '.gitmodules', 'submod2' ])
    r1.push()

    self.assertEqual( sub_repo2_rev1, r1.submodule_status_one('submod2').revision )
    
    sub_repo1_rev2 = sub_repo1.add_file('sub_kiwi1.txt', 'this is sub_kiwi1.txt', push = True)

    self.assertEqual( sub_repo1_rev1, r1.submodule_status_one('submod1').revision )

    git_util.repo_update_submodule(r1.address, 'submod1', 'master', sub_repo1_rev2, False)

    r1.pull()

    r1.submodule_init(submodule = 'submod1')
    
    self.assertEqual( sub_repo1_rev2, r1.submodule_status_one('submod1').revision )


    sub_repo2_rev2 = sub_repo2.add_file('sub_kiwi2.txt', 'this is sub_kiwi2.txt', push = True)
    self.assertEqual( sub_repo2_rev1, r1.submodule_status_one('submod2').revision )

    git_util.repo_update_submodule(r1.address, 'submod2', 'master', sub_repo2_rev2, False)
    
    r1.pull()

    r1.submodule_init(submodule = 'submod2')

    self.assertEqual( sub_repo2_rev2, r1.submodule_status_one('submod2').revision )
    
  @git_temp_home_func()
  def test_no_change(self):
    sub_content = [
      'file subfoo.txt "this is subfoo" 644',
    ]
    sub_repo = self._make_repo(remote = True, content = sub_content, prefix = '-mod-')
    rev1 = sub_repo.last_commit_hash(short_hash = True)
    
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r1 = self._make_repo(remote = True, content = content, prefix = '-main-')
    self.assertEqual( [ 'foo.txt' ], r1.find_all_files() )

    r1.submodule_add(sub_repo.address, 'submod1')
    r1.commit('add mod submodule', '.')
    r1.push()

    self.assertEqual( rev1, r1.submodule_status_one('submod1').revision )
    
    git_util.repo_update_submodule(r1.address, 'submod1', 'master', rev1, False)

    r1.pull()

    r1.submodule_init(submodule = 'submod1')
    
    self.assertEqual( rev1, r1.submodule_status_one('submod1').revision )

  def _make_repo(self, remote = True, content = None, prefix = None, commit_message = None):
    return git_temp_repo(remote = remote, content = content, prefix = prefix,
                         debug = self.DEBUG, commit_message = commit_message)

if __name__ == '__main__':
  unit_test.main()

  
