#!/usr/bin/env python
# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-


from os import path
from bes.fs.file_util import file_util
from bes.testing.unit_test import unit_test
from bes.git.git_util import git_util
from bes.git.git_commit_info import git_commit_info
from bes.git.git_temp_repo import git_temp_repo
from bes.git.git_unit_test import git_temp_home_func

from bes.files.find.bf_file_finder import bf_file_finder

class test_git_util(unit_test):

  @git_temp_home_func()
  def test_repo_greatest_tag(self):
    r = git_temp_repo(debug = self.DEBUG)
    r.add_file('readme.txt', 'readme is good')
    r.push('origin', 'master')
    r.tag('1.0.0')
    r.push_tag('1.0.0')
    self.assertEqual( '1.0.0', git_util.repo_greatest_tag(r.address).name )
    r.tag('1.0.1')
    r.push_tag('1.0.1')
    self.assertEqual( '1.0.1', git_util.repo_greatest_tag(r.address).name )

  @git_temp_home_func()
  def test_repo_bump_tag(self):
    r1 = git_temp_repo(debug = self.DEBUG)
    r2 = r1.make_temp_cloned_repo()
    r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')

    rv = git_util.repo_bump_tag(r1.address, None, False)
    self.assertEqual( ( None, '1.0.0' ), rv )
    r2.pull()
    self.assertEqual( '1.0.0', r2.greatest_local_tag().name )

    rv = git_util.repo_bump_tag(r1.address, None, False)
    self.assertEqual( ( '1.0.0', '1.0.1' ), rv )
    r2.pull()
    self.assertEqual( '1.0.1', r2.greatest_local_tag().name )

    rv = git_util.repo_bump_tag(r1.address, None, False)
    self.assertEqual( ( '1.0.1', '1.0.2' ), rv )
    r2.pull()
    self.assertEqual( '1.0.2', r2.greatest_local_tag().name )

  @git_temp_home_func()
  def test_repo_bump_tag_dry_run(self):
    r1 = git_temp_repo(debug = self.DEBUG)
    r2 = r1.make_temp_cloned_repo()
    r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')

    rv = git_util.repo_bump_tag(r1.address, None, True)
    self.assertEqual( ( None, '1.0.0' ), rv )
    r2.pull()
    self.assertEqual( None, r2.greatest_local_tag() )

  @git_temp_home_func()
  def test_repo_bump_tag_single_number(self):
    r1 = git_temp_repo(debug = self.DEBUG)
    r2 = r1.make_temp_cloned_repo()
    r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')
    r1.tag('666')
    r1.push_tag('666')

    git_util.repo_bump_tag(r1.address, None, False)
    r2.pull()
    self.assertEqual( '667', r2.greatest_local_tag().name )

    git_util.repo_bump_tag(r1.address, None, False)
    r2.pull()
    self.assertEqual( '668', r2.greatest_local_tag().name )

  @git_temp_home_func()
  def test_find_git_dirs(self):
    config = '''\
add commit1 commit1
  kiwi.txt: this is kiwi.txt
add commit2 commit2
  lemon.txt: this is lemon.txt
'''
    tmp_dir = path.join(self.make_temp_dir(), 'repos')
    
    r1 = git_temp_repo(remote = True, debug = self.DEBUG, config = config, prefix = 'r1-', where = tmp_dir)
    r2 = git_temp_repo(remote = True, debug = self.DEBUG, config = config, prefix = 'r2-', where = tmp_dir)
    r3 = git_temp_repo(remote = True, debug = self.DEBUG, config = config, prefix = 'r3-', where = tmp_dir)

    self.assertEqual( [
      r1.root,
      r2.root,
      r3.root,
    ], git_util.find_git_dirs(tmp_dir) )
    
if __name__ == '__main__':
  unit_test.main()
