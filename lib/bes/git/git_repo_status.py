# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check

class git_repo_status(namedtuple('git_repo_status', 'change_status, branch_status, active_branch, last_commit')):
  'A class to encapsulate everything about the status of a git repo.'

  def __new__(clazz, change_status, branch_status, active_branch, last_commit):
    check.check_git_status_list(change_status)
    check.check_git_branch_status(branch_status)
    check.check_string(active_branch)
    check.check_git_commit_info(last_commit)

    return clazz.__bases__[0].__new__(clazz,
                                      change_status,
                                      branch_status,
                                      active_branch,
                                      last_commit)

check.register_class(git_repo_status, include_seq = False)
