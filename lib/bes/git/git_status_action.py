#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.enum_util.checked_enum import checked_enum

class git_status_action(checked_enum):
  ADDED = 'A'
  COPIED = 'C'
  DELETED = 'D'
  MODIFIED = 'M'
  RENAMED = 'R'
  UNMERGED = 'U'
  UNTRACKED = '??'

check.register_class(git_status_action,
                     include_seq = False,
                     cast_func = git_status_action.parse)
