#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import multiprocessing

from bes.fs.file_util import file_util
from bes.git.git import git
from bes.git.git_error import git_error
from bes.git.git_repo import git_repo
from bes.git.git_temp_repo import git_temp_repo
from bes.git.git_unit_test import git_temp_home_func
from bes.git.git_operation_base import git_operation_base
from bes.testing.unit_test import unit_test
from bes.text.line_break import line_break

class test_git_repo_operation(unit_test):

  def _make_repo(self, remote = True, content = None, prefix = None, commit_message = None):
    return git_temp_repo(remote = remote, content = content, prefix = prefix,
                         debug = self.DEBUG, commit_message = commit_message)

  @git_temp_home_func()
  def test_operation_with_reset_basic(self):
    r1 = self._make_repo(prefix = 'operation_with_reset_basic')
    r1.write_temp_content([
      'file foo.txt "this is foo" 644',
    ])
    r1.add([ 'foo.txt' ])
    r1.commit('add foo.txt', [ 'foo.txt' ])
    r1.push('origin', 'master')

    r2 = r1.make_temp_cloned_repo()

    def _op(repo):
      repo.write_temp_content([
        'file bar.txt "this is bar" 644',
      ])
      repo.add('.')
    r2.operation_with_reset(_op, 'add bar.txt')
    self.assertEqual( 'this is foo', r2.read_file('foo.txt', codec = 'utf8') )
    self.assertEqual( 'this is bar', r2.read_file('bar.txt', codec = 'utf8') )

    r3 = r1.make_temp_cloned_repo()
    self.assertEqual( 'this is foo', r3.read_file('foo.txt', codec = 'utf8') )
    self.assertEqual( 'this is bar', r3.read_file('bar.txt', codec = 'utf8') )

  @git_temp_home_func()
  def test_operation_with_reset_basic_interface(self):
    r1 = self._make_repo(prefix = 'operation_with_reset_basic_interface')
    r1.write_temp_content([
      'file foo.txt "this is foo" 644',
    ])
    r1.add([ 'foo.txt' ])
    r1.commit('add foo.txt', [ 'foo.txt' ])
    r1.push('origin', 'master')

    r2 = r1.make_temp_cloned_repo()

    class _op(git_operation_base):
      def run(op_self, repo):
        repo.write_temp_content([
          'file bar.txt "this is bar" 644',
         ])
        repo.add('.')
    r2.operation_with_reset(_op(), 'add bar.txt')
    self.assertEqual( 'this is foo', r2.read_file('foo.txt', codec = 'utf8') )
    self.assertEqual( 'this is bar', r2.read_file('bar.txt', codec = 'utf8') )

    r3 = r1.make_temp_cloned_repo()
    self.assertEqual( 'this is foo', r3.read_file('foo.txt', codec = 'utf8') )
    self.assertEqual( 'this is bar', r3.read_file('bar.txt', codec = 'utf8') )

  @git_temp_home_func()
  def test_operation_with_reset_seq_interface(self):
    r1 = self._make_repo(prefix = 'operation_with_reset_seq_interface')
    r1.write_temp_content([
      'file foo.txt "this is foo" 644',
    ])
    r1.add([ 'foo.txt' ])
    r1.commit('add foo.txt', [ 'foo.txt' ])
    r1.push('origin', 'master')

    r2 = r1.make_temp_cloned_repo()

    class _op1(git_operation_base):
      def run(op_self, repo):
        repo.write_temp_content([
          'file kiwi.txt "this is kiwi" 644',
         ])
        repo.add('.')
    class _op2(git_operation_base):
      def run(op_self, repo):
        repo.write_temp_content([
          'file apple.txt "this is apple" 644',
         ])
        repo.add('.')
    ops = [ _op1(), _op2() ]
    r2.operation_with_reset(ops, 'add kiwi.txt')
    self.assertEqual( 'this is foo', r2.read_file('foo.txt', codec = 'utf8') )
    self.assertEqual( 'this is kiwi', r2.read_file('kiwi.txt', codec = 'utf8') )
    self.assertEqual( 'this is apple', r2.read_file('apple.txt', codec = 'utf8') )

    r3 = r1.make_temp_cloned_repo()
    self.assertEqual( 'this is foo', r3.read_file('foo.txt', codec = 'utf8') )
    self.assertEqual( 'this is kiwi', r3.read_file('kiwi.txt', codec = 'utf8') )
    self.assertEqual( 'this is apple', r3.read_file('apple.txt', codec = 'utf8') )
    
  @git_temp_home_func()
  def test_operation_with_reset_with_conflict(self):
    r1 = self._make_repo(prefix = 'operation_with_reset_with_conflict')
    r1.write_temp_content([
      'file foo.txt "this is foo" 644',
    ])
    r1.add([ 'foo.txt' ])
    r1.commit('add foo.txt', [ 'foo.txt' ])
    r1.push('origin', 'master')

    r2 = r1.make_temp_cloned_repo()
    r3 = r1.make_temp_cloned_repo()

    def _op2(repo):
      repo.write_temp_content([
        'file foo.txt "this is foo 2" 644',
      ])
    r2.operation_with_reset(_op2, 'hack foo.txt to 2')

    def _op3(repo):
      repo.write_temp_content([
        'file foo.txt "this is foo 3" 644',
      ])
    r3.operation_with_reset(_op3, 'hack foo.txt to 3')
    self.assertEqual( 'this is foo 3', r3.read_file('foo.txt', codec = 'utf8') )

    r4 = r1.make_temp_cloned_repo()
    self.assertEqual( 'this is foo 3', r4.read_file('foo.txt', codec = 'utf8') )

  @staticmethod
  def _worker_test_operation_with_reset_with_multiprocess_conflict(clazz, n, address):
    worker_tmp_root = clazz.make_temp_dir(suffix = 'worker-{}'.format(n))
    worker_repo = git_repo(worker_tmp_root, address = address)
    worker_repo.clone_or_pull()
    worker_repo.checkout('master')
      
    def _op(repo):
      old_content = repo.read_file('foo.txt', codec = 'utf8')
      new_content = '{}\nworker {}'.format(old_content, n)
      fp = repo.file_path('foo.txt')
      file_util.save(fp, content = new_content, codec = 'utf8', mode = 0o644)
        
    worker_repo.operation_with_reset(_op, 'from worker {}'.format(n))
    file_util.remove(worker_tmp_root)
    
  @git_temp_home_func()
  def test_operation_with_reset_with_multiprocess_conflict(self):
    '''
    Create a bunch of processes trying to push to the same repo.
    This sometimes creates a git locking issue and tests the operation push retry code.
    '''
    r1 = self._make_repo(prefix = 'operation_with_reset_with_multiprocess_conflict')
    r1.write_temp_content([
      'file foo.txt "_foo" 644',
    ])
    r1.add([ 'foo.txt' ])
    r1.commit('add foo.txt', [ 'foo.txt' ])
    r1.push('origin', 'master')

    num_jobs = 9
    
    jobs = []
    for i in range(num_jobs):
      p = multiprocessing.Process(target = self._worker_test_operation_with_reset_with_multiprocess_conflict, args = ( self.__class__, i, r1.address ))
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
    ], sorted(r2.read_file('foo.txt', codec = 'utf8').split(line_break.DEFAULT_LINE_BREAK)) )

  @git_temp_home_func()
  def test_operation_with_reset_wrong_function_args(self):
    r1 = self._make_repo(prefix = 'operation_with_reset_wrong_function_args')
    r1.write_temp_content([
      'file foo.txt "this is foo" 644',
    ])
    r1.add([ 'foo.txt' ])
    r1.commit('add foo.txt', [ 'foo.txt' ])
    r1.push('origin', 'master')

    r2 = r1.make_temp_cloned_repo()

    def _op(repo, bad_arg):
      pass
    with self.assertRaises(git_error) as ctx:
      r2.operation_with_reset(_op, 'add bar.txt')
    
if __name__ == '__main__':
  unit_test.main()
