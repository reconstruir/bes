#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path, unittest
from bes.fs import file_util, temp_file

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

if __name__ == "__main__":
  unittest.main()
