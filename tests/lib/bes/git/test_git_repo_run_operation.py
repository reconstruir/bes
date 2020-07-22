#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import multiprocessing

from bes.testing.unit_test import unit_test

from bes.fs.file_util import file_util
from bes.git.git_repo import git_repo
from bes.git.git_repo_operation_options import git_repo_operation_options
from bes.git.git_temp_repo import git_temp_repo
from bes.git.git_unit_test import git_temp_home_func
from bes.git.git_util import git_util

class test_git_repo_run_operation(unit_test):
  
  @git_temp_home_func()
  def test_basic(self):
    r = git_temp_repo(debug = self.DEBUG)
    r.add_file('kiwi.txt', content = 'this is kiwi.txt', mode = 0o0644)
    r.push('origin', 'master')
    def _op(repo):
      r.add_file('melon.txt', content = 'this is melon.txt', mode = 0o0644,
                 commit = False, push = False)
    git_util.repo_run_operation(r.address, _op, 'add melon.txt', options = None)
    self.assertEqual( 'this is melon.txt', r.read_file('melon.txt') )
    
  @git_temp_home_func()
  def test_basic_dry_run(self):
    r = git_temp_repo(debug = self.DEBUG)
    r.add_file('kiwi.txt', content = 'this is kiwi.txt', mode = 0o0644)
    r.push('origin', 'master')
    def _op(repo):
      r.add_file('melon.txt', content = 'this is melon.txt', mode = 0o0644,
                 commit = False, push = False)
    options = git_repo_operation_options(dry_run = True)
    git_util.repo_run_operation(r.address, _op, 'add melon.txt', options = options)
    r.pull()
    self.assertFalse( r.has_file('melon.txt') )

  @git_temp_home_func()
  def test_multiprocess_conflict(self):
    '''
    Create a bunch of processes trying to push to the same repo.
    This sometimes creates a git locking issue and tests the operation push retry code.
    '''
    r1 = git_temp_repo(debug = self.DEBUG)
    r1.write_temp_content([
      'file foo.txt "_foo" 644',
    ])
    r1.add([ 'foo.txt' ])
    r1.commit('add foo.txt', [ 'foo.txt' ])
    r1.push('origin', 'master')

    def worker(n):
      def _op(repo):
        old_content = repo.read_file('foo.txt', codec = 'utf8')
        new_content = '{}\nworker {}'.format(old_content, n)
        fp = repo.file_path('foo.txt')
        file_util.save(fp, content = new_content, codec = 'utf8', mode = 0o644)
        
      git_util.repo_run_operation(r1.address, _op, 'from worker {}'.format(n), options = None)

    num_jobs = 9
    
    jobs = []
    for i in range(num_jobs):
      p = multiprocessing.Process(target = worker, args = (i, ))
      jobs.append(p)
      p.start()

    for job in jobs:
      job.join()

    r2 = r1.make_temp_cloned_repo()
    self.assertEqual( [
      '_foo',
      'worker 0',
      'worker 1',
      'worker 2',
      'worker 3',
      'worker 4',
      'worker 5',
      'worker 6',
      'worker 7',
      'worker 8',
    ], sorted(r2.read_file('foo.txt', codec = 'utf8').split('\n')) )
    
if __name__ == '__main__':
  unit_test.main()
