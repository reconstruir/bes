#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum_util.checked_enum import checked_enum

class git_status_action(checked_enum):
  ADDED = 'A'
  ADDED_MODIFIED = 'AM'
  COPIED = 'C'
  DELETED = 'D'
  MODIFIED = 'M'
  RENAMED = 'R'
  RENAMED_MODIFIED = 'RM'
  UNMERGED = 'U'
  UNTRACKED = '??'

git_status_action.register_check_class()
