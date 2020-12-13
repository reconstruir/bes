#!/usr/bin/env python
# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs.temp_file import temp_file
from bes.git.git_temp_repo import git_temp_repo
from bes.git.git_unit_test import git_temp_home_func
from bes.git.git_repo_document_db import git_repo_document_db

import multiprocessing


class test_git_repo_document_db(unit_test):

  @git_temp_home_func()
  def test_the_basics(self):
    # Create an empty temporary repo for the test. You've got to add a
    # dummy file, otherwise the push won't work and the master branch won't
    # be created. add_file does the commit.
    repo = git_temp_repo(debug=self.DEBUG)
    repo.add_file('dummy.txt', 'dummy')
    repo.push('origin', 'master')
    tmp_working_dir = temp_file.make_temp_dir(delete=not self.DEBUG)

    # Set up the test DB.
    db = git_repo_document_db(tmp_working_dir, repo.address, 'master')

    # Use the DB to store a change to the file.
    db.update_document('testdoc.txt', lambda content: content + 'a\n', 'test commit message')

    # Now retrieve what we stored.
    content = db.load_document('testdoc.txt')
    self.assertEqual(content, 'a\n')

    # And check that the file really exists via the repo interface and has the
    # content in it. The repo file side effect is part of the contract.
    repo.pull()
    self.assertEqual('a\n', repo.read_file('testdoc.txt'))

    # Now modify the file further and retrieve it again.
    db.update_document('testdoc.txt', lambda content: content + 'b\n', 'test commit message 2')
    content = db.load_document('testdoc.txt')
    self.assertEqual(content, 'a\nb\n')
    repo.pull()
    self.assertEqual('a\nb\n', repo.read_file('testdoc.txt'))

    # Try replacing everything.
    db.update_document('testdoc.txt', lambda content: 'foo', 'test commit message 3')
    content = db.load_document('testdoc.txt')
    self.assertEqual(content, 'foo')
    repo.pull()
    self.assertEqual('foo', repo.read_file('testdoc.txt'))

  @git_temp_home_func()
  def test_conflict_retry(self):
    # Create a fresh repo with a master branch.
    repo = git_temp_repo(debug=self.DEBUG)
    repo.add_file('dummy.txt', 'dummy')
    repo.push('origin', 'master')

    #try_count = []

    from conflict_retry_worker import worker
    
    # This test runs numerous threads that all attempt to access the repository
    # at the same time. The repository code will only do 10 retries, so if you
    # try to do more than 9 jobs or so, updates will start to fail and the test
    # will not pass.
    num_jobs = 9
    jobs = []
    for i in range(num_jobs):
      p = multiprocessing.Process(target = worker, args = ( i, repo.address, self.DEBUG ))
      jobs.append(p)
      #try_count.append(0)
      p.start()

    for job in jobs:
      job.join()

    # Now get the file from the remote into the main thread's local repo and
    # check the results.
    repo.pull()
    contents = repo.read_file('retries.txt')
    actual = sorted(contents.split('\n'))
    expected = [str(n) for n in range(num_jobs)]
    self.assertEqual(actual, expected)


if __name__ == '__main__':
  unit_test.main()
