# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check
from bes.common.string_util import string_util

from .git_error import git_error

#      'status': status,
#      'last_commit': last_commit_hash,
#      'branch_status': { 'ahead': branch_status.ahead, 'behind': branch_status.behind },
#      'active_branch': git.active_branch(git_dir),
#      'changes': changes,
#      'remote_origin_url': git.remote_origin_url(git_dir),

class git_repo_status(namedtuple('git_repo_status', 'change_status, branch_status, active_branch, last_commit')):
  'A class to encapsulate everything about the status of a git repo.'

  def __new__(clazz, change_status, branch_status, active_branch, last_commit):
    check.check_git_status_list(change_status)
    check.check_git_branch_status(branch_status)
    check.check_string(active_branch)
    check.check_string(last_commit)

    return clazz.__bases__[0].__new__(clazz, change_status, branch_status, active_branch, last_commit)

  def __str__(self):
    return 'foo'
  #ss = '-' if self.is_pointer else '*'
  #  return '{} {} {}'.format(self.oid, ss, self.filename)

  @property
  def oid_short(self):
    'Return the short object id'
    return self.oid[0:10]

  @classmethod
  def get_status(self, root_dir):
    'Get the repo status for one git project'
    status = git.status(git_dir, [ '.' ])
    last_commit_hash = git.last_commit_hash(git_dir, short_hash = True)
    if not no_remote:
      git.remote_update(git_dir)
    branch_status = git.branch_status(git_dir)
    if untracked:
      changes = status
    else:
      changes = [ item for item in status if '?' not in item.action ]
    result = {
      'git_dir': git_dir,
      'status': status,
      'last_commit': last_commit_hash,
      'branch_status': { 'ahead': branch_status.ahead, 'behind': branch_status.behind },
      'active_branch': git.active_branch(git_dir),
      'changes': changes,
      'remote_origin_url': git.remote_origin_url(git_dir),
    } 
    return result
  
check.register_class(git_repo_status, include_seq = False)
