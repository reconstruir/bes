#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path, unittest
from bes.fs import file_util, temp_file
from bes.archive import archiver

from bes.git import git, status

class test_git(unittest.TestCase):

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
    
if __name__ == "__main__":
  unittest.main()
