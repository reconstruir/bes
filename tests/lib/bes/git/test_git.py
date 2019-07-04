#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#
import os.path as path, os, unittest

from bes.testing.unit_test import unit_test
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.archive.archiver import archiver
from bes.git.git_unit_test import git_temp_home_func
from bes.system.env_override import env_override_temp_home_func

from bes.git.git import git
from bes.git.git_status import git_status

class test_git(unit_test):

  def _create_tmp_repo(self):
    tmp_repo = self.make_temp_dir()
    git.init(tmp_repo)
    return tmp_repo

  def _create_tmp_files(self, tmp_repo):
    foo = path.join(tmp_repo, 'foo.txt')
    bar = path.join(tmp_repo, 'bar.txt')
    file_util.save(foo, content = 'foo.txt\n')
    file_util.save(bar, content = 'bar.txt\n')
    return [ 'bar.txt', 'foo.txt' ]

  @git_temp_home_func()
  def test_add(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    expected_status = [ git_status(git_status.ADDED, f) for f in new_files ]
    actual_status = git.status(tmp_repo, '.')
    self.assertEqual( expected_status, actual_status )

  @git_temp_home_func()
  def test_commit(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    git.commit(tmp_repo, 'nomsg\n', '.')

  @git_temp_home_func()
  def test_clone(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    git.commit(tmp_repo, 'nomsg\n', '.')

    cloned_tmp_repo = self.make_temp_dir()
    git.clone(tmp_repo, cloned_tmp_repo)

    expected_cloned_files = [ path.join(cloned_tmp_repo, path.basename(f)) for f in new_files ]

    for f in expected_cloned_files:
      self.assertTrue( path.exists(f) )

  @git_temp_home_func()
  def test_clone_or_pull(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    git.commit(tmp_repo, 'nomsg\n', '.')

    cloned_tmp_repo = self.make_temp_dir()
    git.clone(tmp_repo, cloned_tmp_repo)

    expected_cloned_files = [ path.join(cloned_tmp_repo, path.basename(f)) for f in new_files ]

    for f in expected_cloned_files:
      self.assertTrue( path.exists(f) )

  @git_temp_home_func()
  def test_tag(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    git.commit(tmp_repo, 'nomsg\n', '.')
    git.tag(tmp_repo, '1.0.0')
    self.assertEqual( [ '1.0.0' ], git.list_local_tags(tmp_repo) )
    git.tag(tmp_repo, '1.0.1')
    self.assertEqual( [ '1.0.0', '1.0.1' ], git.list_local_tags(tmp_repo) )
    git.tag(tmp_repo, '1.0.9')
    git.tag(tmp_repo, '1.0.10')
    self.assertEqual( [ '1.0.0', '1.0.1', '1.0.9', '1.0.10' ], git.list_local_tags(tmp_repo) )
    self.assertEqual( '1.0.10', git.greatest_local_tag(tmp_repo) )
    self.assertEqual( ['1.0.0', '1.0.1', '1.0.10', '1.0.9'], git.list_local_tags(tmp_repo, lexical = True) )
    self.assertEqual( [ '1.0.10', '1.0.9', '1.0.1', '1.0.0' ], git.list_local_tags(tmp_repo, reverse = True) )

  @git_temp_home_func()
  def test_delete_local_tag(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    git.commit(tmp_repo, 'nomsg\n', '.')
    git.tag(tmp_repo, '1.0.0')
    git.tag(tmp_repo, '1.0.1')
    git.tag(tmp_repo, '1.0.9')
    git.tag(tmp_repo, '1.0.10')
    self.assertEqual( [ '1.0.0', '1.0.1', '1.0.9', '1.0.10' ], git.list_local_tags(tmp_repo) )
    git.delete_local_tag(tmp_repo, '1.0.9')
    self.assertEqual( [ '1.0.0', '1.0.1', '1.0.10' ], git.list_local_tags(tmp_repo) )
    git.delete_local_tag(tmp_repo, '1.0.0')
    self.assertEqual( [ '1.0.1', '1.0.10' ], git.list_local_tags(tmp_repo) )
    git.delete_local_tag(tmp_repo, '1.0.10')
    self.assertEqual( [ '1.0.1' ], git.list_local_tags(tmp_repo) )
    git.delete_local_tag(tmp_repo, '1.0.1')
    self.assertEqual( [], git.list_local_tags(tmp_repo) )

  @git_temp_home_func()
  def test_tag_allow_downgrade_error(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    git.commit(tmp_repo, 'nomsg\n', '.')
    git.tag(tmp_repo, '1.0.100')
    self.assertEqual( '1.0.100', git.greatest_local_tag(tmp_repo) )
    with self.assertRaises(ValueError) as ctx:
      git.tag(tmp_repo, '1.0.99')
    
  @git_temp_home_func()
  def test_tag_allow_downgrade(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    git.commit(tmp_repo, 'nomsg\n', '.')
    git.tag(tmp_repo, '1.0.100')
    self.assertEqual( '1.0.100', git.greatest_local_tag(tmp_repo) )
    git.tag(tmp_repo, '1.0.99', allow_downgrade = True)
    self.assertEqual( '1.0.100', git.greatest_local_tag(tmp_repo) )
    self.assertEqual( [ '1.0.99', '1.0.100' ], git.list_local_tags(tmp_repo) )
    
  @git_temp_home_func()
  def test_read_gitignore(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    git.commit(tmp_repo, 'nomsg\n', '.')
    self.assertEqual( None, git.read_gitignore(tmp_repo) )
    
    file_util.save(path.join(tmp_repo, '.gitignore'), content = 'foo.txt\nbar.txt\nBUILD\n*~\n')
    git.add(tmp_repo, '.gitignore')
    git.commit(tmp_repo, 'add .gitignore\n', '.')
    self.assertEqual( [
      'foo.txt',
      'bar.txt',
      'BUILD',
      '*~',
      ], git.read_gitignore(tmp_repo) )
    
  @git_temp_home_func()
  def test_archive_local_repo(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    git.commit(tmp_repo, 'nomsg\n', '.')
    tmp_archive = self.make_temp_file()
    git.archive(tmp_repo, 'master', 'foo', tmp_archive)
    self.assertEqual( [
      'foo-master/',
      'foo-master/bar.txt',
      'foo-master/foo.txt',
    ], archiver.members(tmp_archive) )
    
  @git_temp_home_func()
  def test_archive_local_repo_untracked(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    git.commit(tmp_repo, 'nomsg\n', '.')
    file_util.save(path.join(tmp_repo, 'kiwi.txt'), content = 'this is kiwi.txt\n')
    tmp_archive = self.make_temp_file()
    git.archive(tmp_repo, 'master', 'foo', tmp_archive, untracked = True)
    self.assertEqual( [
      'foo-master/',
      'foo-master/bar.txt',
      'foo-master/foo.txt',
      'foo-master/kiwi.txt',
    ], archiver.members(tmp_archive) )
    
  @git_temp_home_func()
  def test_archive_local_repo_untracked_gitignore(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    git.commit(tmp_repo, 'nomsg\n', '.')
    file_util.save(path.join(tmp_repo, 'kiwi.txt'), content = 'this is kiwi.txt\n')
    file_util.save(path.join(tmp_repo, 'ignored.txt'), content = 'this is ignored.txt\n')
    file_util.save(path.join(tmp_repo, '.gitignore'), content = 'ignored.txt\n')
    tmp_archive = self.make_temp_file()
    git.archive(tmp_repo, 'master', 'foo', tmp_archive, untracked = True)
    self.assertEqual( [
      'foo-master/',
      'foo-master/.gitignore',
      'foo-master/bar.txt',
      'foo-master/foo.txt',
      'foo-master/kiwi.txt',
    ], archiver.members(tmp_archive) )

  @env_override_temp_home_func()
  def test_config(self):
    self.assertEqual( None, git.config_get_value('user.name') )
    self.assertEqual( None, git.config_get_value('user.email') )

    git.config_set_value('user.name', 'foo bar')
    self.assertEqual( 'foo bar', git.config_get_value('user.name') )
      
    git.config_set_value('user.email', 'foo@example.com')
    self.assertEqual( 'foo@example.com', git.config_get_value('user.email') )

    self.assertEqual( ( 'foo bar', 'foo@example.com' ), git.config_get_identity() )

    git.config_set_identity('green kiwi', 'kiwi@example.com')
    self.assertEqual( ( 'green kiwi', 'kiwi@example.com' ), git.config_get_identity() )

    git.config_unset_value('user.email')
    self.assertEqual( ( 'green kiwi', None ), git.config_get_identity() )

    git.config_unset_value('user.name')
    self.assertEqual( ( None, None ), git.config_get_identity() )
      
  @git_temp_home_func()
  def test_has_changes(self):
    tmp_repo = self._create_tmp_repo()
    self.assertFalse( git.has_changes(tmp_repo) )
    new_files = self._create_tmp_files(tmp_repo)
    self.assertFalse( git.has_changes(tmp_repo) )
    git.add(tmp_repo, new_files)
    self.assertTrue( git.has_changes(tmp_repo) )
    git.commit(tmp_repo, 'nomsg\n', '.')
    self.assertFalse( git.has_changes(tmp_repo) )
    
  @git_temp_home_func()
  def test_has_changes(self):
    tmp_repo = self._create_tmp_repo()
    self.assertFalse( git.has_changes(tmp_repo) )
    new_files = self._create_tmp_files(tmp_repo)
    self.assertFalse( git.has_changes(tmp_repo) )
    git.add(tmp_repo, new_files)
    self.assertTrue( git.has_changes(tmp_repo) )
    git.commit(tmp_repo, 'nomsg\n', '.')
    self.assertFalse( git.has_changes(tmp_repo) )

  @git_temp_home_func()
  def test_has_determine_where(self):
    self.assertEqual( 'both', git.determine_where(True, True) )
    self.assertEqual( 'local', git.determine_where(True, False) )
    self.assertEqual( 'remote', git.determine_where(False, True) )
    self.assertEqual( 'both', git.determine_where(None, None) )

  @git_temp_home_func()
  def test_resolve_address(self):
    self.assertEqual( 'https://github.com/git/git.git', git.resolve_address('https://github.com/git/git.git') )
    self.assertEqual( 'git@github.com/git/git.git', git.resolve_address('git@github.com/git/git.git') )
    tmp_repo = path.expanduser('~/minerepo')
    file_util.mkdir(tmp_repo)
    git.init(tmp_repo)
    self.assertEqual( tmp_repo, git.resolve_address('~/minerepo') )

  @git_temp_home_func()
  def test_is_long_hash(self):
    self.assertTrue( git.is_long_hash('cd138635e1a94a6f2da6acbce3e2f2d584121d28') )
    self.assertFalse( git.is_long_hash('zd138635e1a94a6f2da6acbce3e2f2d584121d28') )
    self.assertFalse( git.is_long_hash('cd13863') )

  @git_temp_home_func()
  def test_is_short_hash(self):
    self.assertTrue( git.is_short_hash('cd13863') )
    self.assertFalse( git.is_short_hash('cd138635e1a94a6f2da6acbce3e2f2d584121d28') )
    self.assertFalse( git.is_short_hash('zd13863') )
      
if __name__ == '__main__':
  unit_test.main()
