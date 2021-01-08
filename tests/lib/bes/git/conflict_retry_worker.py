# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.fs.temp_file import temp_file
from bes.git.git_unit_test import git_temp_home_func
from bes.git.git_repo_document_db import git_repo_document_db

import multiprocessing

@git_temp_home_func()
def worker(n, address, debug):
  tmp_working_dir = temp_file.make_temp_dir(delete = not debug)
  db = git_repo_document_db(tmp_working_dir, address, 'master')

  def attempt_update(content):

    # If you let this print you will find that it actually does a lot of retries!
    #try_count[n] += 1
    #print 'try count[{}] is {}'.format(n, try_count[n])

    # Since the workers may run in any order, the results could be like
    # '3\n1\n4\n2\n...'
    if content == '':
      return '{}'.format(n)
    return '{}\n{}'.format(content, n)

  db.update_document('retries.txt', attempt_update, 'a commit message')
