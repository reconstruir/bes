#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check
class git_branch_status(namedtuple('git_branch_status', 'ahead, behind')):

  def __new__(clazz, ahead, behind):
    check.check_int(ahead)
    check.check_int(behind)

    return clazz.__bases__[0].__new__(clazz, ahead, behind)

check.register_class(git_branch_status, include_seq = False)
