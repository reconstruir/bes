# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check

from .git_error import git_error

class git_change_info(namedtuple('git_change_info', 'uncommitted, untracked, unpushed')):
  'A class to deal with git head info.'

  def __new__(clazz, uncommitted, untracked, unpushed):
    check.check_bool(uncommitted)
    check.check_bool(untracked)
    check.check_bool(unpushed)
    return clazz.__bases__[0].__new__(clazz, uncommitted, untracked, unpushed)

  def __str__(self):
    return ''

