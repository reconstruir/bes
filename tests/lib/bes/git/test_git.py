#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#
import os.path as path, os, unittest
from bes.fs import file_util, temp_file
from bes.archive import archiver

from bes.git import git, status
from bes.git.git_unit_test import git_unit_test
from bes.git.temp_git_repo import temp_git_repo

class test_git(unittest.TestCase):

  @classmethod
  def setUpClass(clazz):
    git_unit_test.set_identity()

  @classmethod
  def tearDownClass(clazz):
    git_unit_test.unset_identity()

  def _create_tmp_repo(self):
    tmp_repo = temp_file.make_temp_dir()
    git.init(tmp_repo)
    return tmp_repo

  def _create_tmp_files(self, tmp_repo):
    foo = path.join(tmp_repo, 'foo.txt')
    bar = path.join(tmp_repo, 'bar.txt')
    file_util.save(foo, content = 'foo.txt\n')
    file_util.save(bar, content = 'bar.txt\n')
    return [ 'bar.txt', 'foo.txt' ]

  def test_add(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    expected_status = [ status(status.ADDED, f) for f in new_files ]
    actual_status = git.status(tmp_repo, '.')
    self.assertEqual( expected_status, actual_status )

  def test_commit(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    git.commit(tmp_repo, 'nomsg\n', '.')

  def test_clone(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    git.commit(tmp_repo, 'nomsg\n', '.')

    cloned_tmp_repo = temp_file.make_temp_dir()
    git.clone(tmp_repo, cloned_tmp_repo)

    expected_cloned_files = [ path.join(cloned_tmp_repo, path.basename(f)) for f in new_files ]

    for f in expected_cloned_files:
      self.assertTrue( path.exists(f) )

  def test_clone_or_pull(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    git.commit(tmp_repo, 'nomsg\n', '.')

    cloned_tmp_repo = temp_file.make_temp_dir()
    git.clone(tmp_repo, cloned_tmp_repo)

    expected_cloned_files = [ path.join(cloned_tmp_repo, path.basename(f)) for f in new_files ]

    for f in expected_cloned_files:
      self.assertTrue( path.exists(f) )

  def test_tag(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    git.commit(tmp_repo, 'nomsg\n', '.')
    git.tag(tmp_repo, '1.0.0')
    self.assertEqual( [ '1.0.0' ], git.list_tags(tmp_repo) )
    git.tag(tmp_repo, '1.0.1')
    self.assertEqual( [ '1.0.0', '1.0.1' ], git.list_tags(tmp_repo) )
    git.tag(tmp_repo, '1.0.9')
    git.tag(tmp_repo, '1.0.10')
    self.assertEqual( [ '1.0.0', '1.0.1', '1.0.9', '1.0.10' ], git.list_tags(tmp_repo) )
    self.assertEqual( '1.0.10', git.last_tag(tmp_repo) )
    self.assertEqual( ['1.0.0', '1.0.1', '1.0.10', '1.0.9'], git.list_tags(tmp_repo, lexical = True) )
    self.assertEqual( [ '1.0.10', '1.0.9', '1.0.1', '1.0.0' ], git.list_tags(tmp_repo, reverse = True) )

  def test_delete_tag(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    git.commit(tmp_repo, 'nomsg\n', '.')
    git.tag(tmp_repo, '1.0.0')
    git.tag(tmp_repo, '1.0.1')
    git.tag(tmp_repo, '1.0.9')
    git.tag(tmp_repo, '1.0.10')
    self.assertEqual( [ '1.0.0', '1.0.1', '1.0.9', '1.0.10' ], git.list_tags(tmp_repo) )
    git.delete_tag(tmp_repo, '1.0.9')
    self.assertEqual( [ '1.0.0', '1.0.1', '1.0.10' ], git.list_tags(tmp_repo) )
    git.delete_tag(tmp_repo, '1.0.0')
    self.assertEqual( [ '1.0.1', '1.0.10' ], git.list_tags(tmp_repo) )
    git.delete_tag(tmp_repo, '1.0.10')
    self.assertEqual( [ '1.0.1' ], git.list_tags(tmp_repo) )
    git.delete_tag(tmp_repo, '1.0.1')
    self.assertEqual( [], git.list_tags(tmp_repo) )

  def test_delete_remote_tags(self):
    r1 = temp_git_repo.make_temp_repo([ '--bare', '--shared' ])
    r2 = temp_git_repo.make_temp_cloned_repo(r1.root)
    r3 = temp_git_repo.make_temp_cloned_repo(r1.root)
    r2.add_file('readme.txt', 'readme is good')
    r2.push('origin', 'master')
    r2.tag('1.0.0')
    r2.push_tag('1.0.0')
    r2.tag('1.0.1')
    r2.push_tag('1.0.1')
    self.assertEqual( [ '1.0.0', '1.0.1' ], r3.list_remote_tags() )
    r2.delete_tag('1.0.1')
    r2.delete_remote_tag('1.0.1')
    self.assertEqual( [ '1.0.0' ], r3.list_remote_tags() )
    
    
  def test_list_remote_tags(self):
    r1 = temp_git_repo.make_temp_repo([ '--bare', '--shared' ])
    r2 = temp_git_repo.make_temp_cloned_repo(r1.root)
    r3 = temp_git_repo.make_temp_cloned_repo(r1.root)
    r2.add_file('readme.txt', 'readme is good')
    r2.push('origin', 'master')
    r2.tag('1.0.0')
    r2.push_tag('1.0.0')
    r2.tag('1.0.1')
    r2.push_tag('1.0.1')
    self.assertEqual( [ '1.0.0', '1.0.1' ], r3.list_remote_tags() )
    
  def test_tag_allow_downgrade_error(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    git.commit(tmp_repo, 'nomsg\n', '.')
    git.tag(tmp_repo, '1.0.100')
    self.assertEqual( '1.0.100', git.last_tag(tmp_repo) )
    with self.assertRaises(ValueError) as ctx:
      git.tag(tmp_repo, '1.0.99')
    
  def test_tag_allow_downgradex(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    git.commit(tmp_repo, 'nomsg\n', '.')
    git.tag(tmp_repo, '1.0.100')
    self.assertEqual( '1.0.100', git.last_tag(tmp_repo) )
    git.tag(tmp_repo, '1.0.99', allow_downgrade = True)
    self.assertEqual( '1.0.100', git.last_tag(tmp_repo) )
    self.assertEqual( [ '1.0.99', '1.0.100' ], git.list_tags(tmp_repo) )
    
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
    
  def test_archive_local_repo(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    git.commit(tmp_repo, 'nomsg\n', '.')
    tmp_archive = temp_file.make_temp_file()
    git.archive(tmp_repo, 'master', 'foo', tmp_archive)
    self.assertEqual( [
      'foo-master',
      'foo-master/bar.txt',
      'foo-master/foo.txt',
    ], archiver.members(tmp_archive) )
    
  def test_archive_local_repo_untracked(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    git.commit(tmp_repo, 'nomsg\n', '.')
    file_util.save(path.join(tmp_repo, 'kiwi.txt'), content = 'this is kiwi.txt\n')
    tmp_archive = temp_file.make_temp_file()
    git.archive(tmp_repo, 'master', 'foo', tmp_archive, untracked = True)
    self.assertEqual( [
      'foo-master',
      'foo-master/bar.txt',
      'foo-master/foo.txt',
      'foo-master/kiwi.txt',
    ], archiver.members(tmp_archive) )
    
  def test_archive_local_repo_untracked_gitignore(self):
    tmp_repo = self._create_tmp_repo()
    new_files = self._create_tmp_files(tmp_repo)
    git.add(tmp_repo, new_files)
    git.commit(tmp_repo, 'nomsg\n', '.')
    file_util.save(path.join(tmp_repo, 'kiwi.txt'), content = 'this is kiwi.txt\n')
    file_util.save(path.join(tmp_repo, 'ignored.txt'), content = 'this is ignored.txt\n')
    file_util.save(path.join(tmp_repo, '.gitignore'), content = 'ignored.txt\n')
    tmp_archive = temp_file.make_temp_file()
    git.archive(tmp_repo, 'master', 'foo', tmp_archive, untracked = True)
    self.assertEqual( [
      'foo-master',
      'foo-master/.gitignore',
      'foo-master/bar.txt',
      'foo-master/foo.txt',
      'foo-master/kiwi.txt',
    ], archiver.members(tmp_archive) )

  def test_config(self):
    tmp_home = temp_file.make_temp_dir()
    save_home = os.environ['HOME']
    os.environ['HOME'] = tmp_home

    try:
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
      
    finally:
      os.environ['HOME'] = save_home

  def test_bump_tag(self):
    r1 = temp_git_repo.make_temp_repo([ '--bare', '--shared' ])
    r2 = temp_git_repo.make_temp_cloned_repo(r1.root)
    r2.add_file('readme.txt', 'readme is good')
    r2.push('origin', 'master')
    r2.tag('1.0.0')
    r2.push_tag('1.0.0')
    self.assertEqual( '1.0.0', r2.last_tag() )
    r2.bump_tag()

    r3 = temp_git_repo.make_temp_cloned_repo(r1.root)
    self.assertEqual( '1.0.1', r3.last_tag() )

  def test_bump_tag_empty(self):
    r1 = temp_git_repo.make_temp_repo([ '--bare', '--shared' ])
    r2 = temp_git_repo.make_temp_cloned_repo(r1.root)
    r2.add_file('readme.txt', 'readme is good')
    r2.push('origin', 'master')
    self.assertEqual( None, r2.last_tag() )
    r2.bump_tag()

    r3 = temp_git_repo.make_temp_cloned_repo(r1.root)
    self.assertEqual( '1.0.0', r3.last_tag() )
    
  def test_has_changes(self):
    tmp_repo = self._create_tmp_repo()
    self.assertFalse( git.has_changes(tmp_repo) )
    new_files = self._create_tmp_files(tmp_repo)
    self.assertFalse( git.has_changes(tmp_repo) )
    git.add(tmp_repo, new_files)
    self.assertTrue( git.has_changes(tmp_repo) )
    git.commit(tmp_repo, 'nomsg\n', '.')
    self.assertFalse( git.has_changes(tmp_repo) )
    
if __name__ == "__main__":
  unittest.main()
