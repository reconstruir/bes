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
from bes.system.host import host

from bes.git.git import git
from bes.git.git_status import git_status
from bes.git.git_status_action import git_status_action

class test_git(unit_test):

  def _create_tmp_repo(self, *args):
    # make the temp dir predictable on macos
    if host.is_macos():
      d = '/private/tmp'
    else:
      d = None
    tmp_dir = self.make_temp_dir(dir = d)
    git.init(tmp_dir, *args)
    return tmp_dir

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
    expected_status = [ git_status(git_status_action.ADDED, f, None) for f in new_files ]
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
    self.assertEqual( [ '1.0.0' ], git.list_local_tags(tmp_repo).names() )
    git.tag(tmp_repo, '1.0.1')
    self.assertEqual( [ '1.0.0', '1.0.1' ], git.list_local_tags(tmp_repo).names() )
    git.tag(tmp_repo, '1.0.9')
    git.tag(tmp_repo, '1.0.10')
    self.assertEqual( [ '1.0.0', '1.0.1', '1.0.9', '1.0.10' ], git.list_local_tags(tmp_repo).names() )
    self.assertEqual( '1.0.10', git.greatest_local_tag(tmp_repo).name )
    self.assertEqual( ['1.0.0', '1.0.1', '1.0.10', '1.0.9'], git.list_local_tags(tmp_repo, sort_type = 'lexical').names() )
    self.assertEqual( [ '1.0.10', '1.0.9', '1.0.1', '1.0.0' ], git.list_local_tags(tmp_repo, reverse = True).names() )

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
    self.assertEqual( [ '1.0.0', '1.0.1', '1.0.9', '1.0.10' ], git.list_local_tags(tmp_repo).names() )
    git.delete_local_tag(tmp_repo, '1.0.9')
    self.assertEqual( [ '1.0.0', '1.0.1', '1.0.10' ], git.list_local_tags(tmp_repo).names() )
    git.delete_local_tag(tmp_repo, '1.0.0')
    self.assertEqual( [ '1.0.1', '1.0.10' ], git.list_local_tags(tmp_repo).names() )
    git.delete_local_tag(tmp_repo, '1.0.10')
    self.assertEqual( [ '1.0.1' ], git.list_local_tags(tmp_repo).names() )
    git.delete_local_tag(tmp_repo, '1.0.1')
    self.assertEqual( [], git.list_local_tags(tmp_repo).names() )

  @git_temp_home_func()
  def test_tag_allow_downgrade_error(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    git.commit(tmp_repo, 'nomsg\n', '.')
    git.tag(tmp_repo, '1.0.100')
    self.assertEqual( '1.0.100', git.greatest_local_tag(tmp_repo).name )
    with self.assertRaises(ValueError) as ctx:
      git.tag(tmp_repo, '1.0.99')
    
  @git_temp_home_func()
  def test_tag_allow_downgrade(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    git.commit(tmp_repo, 'nomsg\n', '.')
    git.tag(tmp_repo, '1.0.100')
    self.assertEqual( '1.0.100', git.greatest_local_tag(tmp_repo).name )
    git.tag(tmp_repo, '1.0.99', allow_downgrade = True)
    self.assertEqual( '1.0.100', git.greatest_local_tag(tmp_repo).name )
    self.assertEqual( [ '1.0.99', '1.0.100' ], git.list_local_tags(tmp_repo).names() )
    
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
  def test_is_long_hash(self):
    self.assertTrue( git.is_long_hash('cd138635e1a94a6f2da6acbce3e2f2d584121d28') )
    self.assertFalse( git.is_long_hash('zd138635e1a94a6f2da6acbce3e2f2d584121d28') )
    self.assertFalse( git.is_long_hash('cd13863') )

  @git_temp_home_func()
  def test_is_short_hash(self):
    self.assertTrue( git.is_short_hash('cd13863') )
    self.assertFalse( git.is_short_hash('cd138635e1a94a6f2da6acbce3e2f2d584121d28') )
    self.assertFalse( git.is_short_hash('zd13863') )

  @git_temp_home_func()
  def test_is_repo_true(self):
    tmp_repo = self._create_tmp_repo()
    tmp_bare_repo = self._create_tmp_repo('--bare')
    self.assertTrue( git.is_repo(tmp_repo) )
    self.assertFalse( git.is_bare_repo(tmp_repo) )
    
  @git_temp_home_func()
  def test_is_repo_false(self):
    tmp_repo = self.make_temp_dir()
    self.assertFalse( git.is_repo(tmp_repo) )
    
  @git_temp_home_func()
  def test_is_bare_repo_true(self):
    tmp_repo = self._create_tmp_repo()
    tmp_bare_repo = self._create_tmp_repo('--bare')
    self.assertFalse( git.is_bare_repo(tmp_repo) )
    self.assertTrue( git.is_bare_repo(tmp_bare_repo) )
    
  @git_temp_home_func()
  def test_is_bare_repo_false(self):
    tmp_bare_repo = self.make_temp_dir()
    self.assertFalse( git.is_bare_repo(tmp_bare_repo) )

  @git_temp_home_func()
  def test_find_root_dir(self):
    tmp_repo = self._create_tmp_repo()
    self.assertEqual( tmp_repo, git.find_root_dir(start_dir = tmp_repo) )

    d = path.join(tmp_repo, 'foo', 'bar', 'baz')
    file_util.mkdir(d)
    self.assertEqual( tmp_repo, git.find_root_dir(start_dir = d) )

    self.assertEqual( None, git.find_root_dir(self.make_temp_dir()) )
    
if __name__ == '__main__':
  unit_test.main()
