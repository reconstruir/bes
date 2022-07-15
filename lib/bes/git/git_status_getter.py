#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import multiprocessing
import os.path as path
import time
from collections import namedtuple

from bes.thread.thread_pool import thread_pool
from bes.system.log import logger
from ..system.check import check

from .git_error import git_error
from .git_repo import git_repo
from .git_repo_status_options import git_repo_status_options
from .git_util import git_util

class git_status_getter(object):
  'Some higher level git utilities.'

  _log = logger('git')

  def __init__(self):
    pass

  _get_status_item = namedtuple('_get_status_item', 'repo, status')
  @classmethod
  def get_status(clazz, repos, options = None):
    check.check_git_repo_seq(repos)
    check.check_git_repo_status_options(options, allow_none = True)

    options = options or git_repo_status_options()
    
    pool = thread_pool(options.num_jobs)
    queue = multiprocessing.Queue()

    repo_map = {}
    for next_repo in repos:
      if next_repo.root in repo_map:
        raise git_error('Duplicate repo: {}'.format(next_repo.root))
      repo_map[next_repo.root] = next_repo
    
    def _task(task_repo_root_, task_options_):
      clazz._log.log_d('here {}'.format(task_repo_root_))
      task_repo_ = git_repo(task_repo_root_)
      status = None
      for i in range(0, task_options_.num_tries):
        if i > 0:
          time.sleep(task_options_.retry_sleep_time)
        try:
          status = task_repo_.repo_status(options = task_options_)
        except git_error as ex:
          pass
      queue.put( ( task_repo_root_, status ) )
    
    for next_repo in repos:
      pool.add_task(_task, next_repo.root, options)

    result = {}
    for i in range(0, len(repos)):
      next_repo_root, next_status = queue.get()
      assert next_repo_root in repo_map
      next_repo = repo_map[next_repo_root]
      item = clazz._get_status_item(next_repo, next_status)
      yield item

    pool.wait_completion()

  @classmethod
  def _find_git_dirs(clazz, dirs):
    'Return the first .git dir found in any dir in dirs.'
    dirs = object_util.listify(dirs)
    dirs = [ d for d in dirs if path.isdir(d) ]
    possible = []
    result = clazz._find(dirs, '.git', None, None, False)
    result = [ file_util.remove_tail(d, '.git') for d in result ]
    return sorted(result)

  @classmethod
  def _resolve_git_dirs(clazz, dirs, excludes = None, includes = None):
    git_dirs = git_util.find_git_dirs(dirs)
    git_dirs = clazz._filter_git_dirs(git_dirs, excludes, includes)
    return clazz._ignore_git_dirs(git_dirs)

  @classmethod
  def _ignore_git_dirs(clazz, dirs):
    git_dirs = [ d for d in dirs if 'BUILD/' not in d ]
    git_dirs = [ d for d in git_dirs if '.ego_build_list_tmp' not in d ]
    git_dirs = [ d for d in git_dirs if path.isdir(d) ]
    return git_dirs
  
  @classmethod
  def _filter_git_dirs(clazz, dirs, excludes, includes):
    dirs2 = clazz._filter_git_dirs_excludes(dirs, excludes)
    return clazz._filter_git_dirs_includes(dirs2, includes)

  @classmethod
  def _filter_git_dirs_excludes(clazz, dirs, excludes):
    if not excludes:
      return dirs
    result = []
    for i in excludes:
      for d in dirs:
        if i not in d:
          result.append(d)
    return result

  @classmethod
  def _filter_git_dirs_includes(clazz, dirs, includes):
    if not includes:
      return dirs
    result = []
    for d in dirs:
      if clazz._dir_matches_includes(d, includes):
        result.append(d)
    return result

  @classmethod
  def _dir_matches_includes(clazz, d, includes):
    for i in includes:
      if i in d:
        return True
    return False
  
