#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import multiprocessing
from bes.git.git import git
from bes.git.git_temp_repo import git_temp_repo
from bes.git.git_repo import git_repo
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.git.git_unit_test import git_temp_home_func

from bes.testing.unit_test import unit_test

class test_git_push_with_rebase(unit_test):

  @git_temp_home_func()
  def test_simple(self):
    r1 = git_temp_repo(debug = self.DEBUG)
    r1.add_file('coconut', 'coconut')
    r1.push('origin', 'master')

    r2 = git_repo(self.make_temp_dir(), address = r1.address)
    r2.clone_or_pull()
    r2.add_file('kiwi', 'kiwi')
    r1.add_file('lemon', 'lemon')
    r1.push()
    r2.push_with_rebase()
    
    r3 = git_repo(self.make_temp_dir(), address = r1.address)
    r3.clone_or_pull()
    self.assertEqual( [ 'coconut', 'kiwi', 'lemon' ], r3.find_all_files() )
    
  _FRUITS = [
    'apple',
    'blueberry',
    'kiwi',
    'lemon',
    'melon',
    'orange',
    'papaya',
    'pineapple',
    'watermelon',
  ]

  @git_temp_home_func()
  def test_many_concurrent(self):
    '''
    Create a bunch of processes trying to push to the same repo simulataneously.
    This creates git locking issues and exercises the safe_push retry code.
    '''
    r1 = git_temp_repo(debug = self.DEBUG)

    initial_content = self._make_content('coconut')
    r1.add_file('coconut', initial_content)
    r1.push('origin', 'master')
    
    def worker(fruit):
      tmp_dir = self.make_temp_dir()
      content = self._make_content(fruit)
      repo = git_repo(tmp_dir, address = r1.address)
      repo.clone_or_pull()
      repo.add_file(fruit, content = fruit, commit = True)
      repo.push_with_rebase(num_tries = 10, retry_wait_seconds = 0.250)
      return 0

    jobs = []
    for fruit in self._FRUITS:
      p = multiprocessing.Process(target = worker, args = (fruit, ))
      jobs.append(p)
      p.start()

    for job in jobs:
      job.join()

    r2 = git_repo(self.make_temp_dir(), address = r1.address)
    r2.clone_or_pull()

    self.assertEqual( [
      'apple',
      'blueberry',
      'coconut',
      'kiwi',
      'lemon',
      'melon',
      'orange',
      'papaya',
      'pineapple',
      'watermelon',
    ], r2.find_all_files() )

  @classmethod
  def _make_content(clazz, fruit):
    return 'fruit = {}\n'.format(fruit)
    
if __name__ == '__main__':
  unit_test.main()
