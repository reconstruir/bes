#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common import check

class git_address(namedtuple('git_address', 'address, revision')):

  def __new__(clazz, address, revision):
    check.check_string(address)
    check.check_string(revision)
    return clazz.__bases__[0].__new__(clazz, address, revision)
