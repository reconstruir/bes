# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.common.string_util import string_util

from .git_branch import git_branch
from .git_error import git_error
from .git_exe import git_exe

class git_ref(object):
  'A class to deal with git refs.'

  @classmethod
  def branches_for_tag(clazz, root_dir, tag):
    'Return a list of branches that contain the tag.'
    check.check_string(root_dir)
    check.check_string(tag)
    
    ref = 'tags/{}'.format(tag)
    return clazz.branches_for_ref(root_dir, ref)

  @classmethod
  def branches_for_ref(clazz, root_dir, ref):
    'Return a list of branches that contain the ref.'
    check.check_string(root_dir)
    check.check_string(ref)

    rv = git_exe.call_git(root_dir, [ 'branch', '-a', '--verbose', '--contains', ref ])
    lines = git_exe.parse_lines(rv.stdout)
    lines = [ line for line in lines if not '(HEAD detached' in line ]
    branches = [ git_branch.parse_branch(line, 'local') for line in lines ]
    branches = [ branch.name for branch in branches ]
    branches = [ string_util.remove_head(branch, 'remotes/origin/') for branch in branches ]
    blacklist = { 'HEAD' }
    branches = [ branch for branch in branches if branch not in blacklist ]
    return sorted(list(set(branches)))
  
