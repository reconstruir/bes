#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.git import git_util
from bes.git.git_temp_repo import git_temp_repo
from bes.git.git_unit_test import git_unit_test

class test_git_util(unit_test):

  @classmethod
  def setUpClass(clazz):
    git_unit_test.set_identity()

  @classmethod
  def tearDownClass(clazz):
    git_unit_test.unset_identity()
  
  def test_name_from_address(self):
    self.assertEqual( 'bar', git_util.name_from_address('https://foohub.com/myproj/bar.git') )
    self.assertEqual( 'foo-bar-baz', git_util.name_from_address('git@git:foo-bar-baz.git') )

  def test_repo_greatest_tag(self):
    r = git_temp_repo()
    r.add_file('readme.txt', 'readme is good')
    r.push('origin', 'master')
    r.tag('1.0.0')
    r.push_tag('1.0.0')
    self.assertEqual( '1.0.0', git_util.repo_greatest_tag(r.address) )
    r.tag('1.0.1')
    r.push_tag('1.0.1')
    self.assertEqual( '1.0.1', git_util.repo_greatest_tag(r.address) )
    
  def test_repo_bump_tag(self):
    r1 = git_temp_repo()
    r2 = r1.make_temp_cloned_repo()
    r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')

    git_util.repo_bump_tag(r1.address, None, False)
    r2.pull()
    self.assertEqual( '1.0.0', r2.greatest_local_tag() )

    git_util.repo_bump_tag(r1.address, None, False)
    r2.pull()
    self.assertEqual( '1.0.1', r2.greatest_local_tag() )

    git_util.repo_bump_tag(r1.address, None, False)
    r2.pull()
    self.assertEqual( '1.0.2', r2.greatest_local_tag() )
  
  def test_repo_bump_tag_single_number(self):
    r1 = git_temp_repo()
    r2 = r1.make_temp_cloned_repo()
    r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')
    r1.tag('666')
    r1.push_tag('666')

    git_util.repo_bump_tag(r1.address, None, False)
    r2.pull()
    self.assertEqual( '667', r2.greatest_local_tag() )

    git_util.repo_bump_tag(r1.address, None, False)
    r2.pull()
    self.assertEqual( '668', r2.greatest_local_tag() )
  
if __name__ == '__main__':
  unit_test.main()
