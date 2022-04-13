#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from bes.git.git import git

class git_address(namedtuple('git_address', 'address, revision')):

  def __new__(clazz, address, revision):
    check.check_string(address)
    check.check_string(revision)
    return clazz.__bases__[0].__new__(clazz, address, revision)

  @property
  def resolved_revision(self):
    if self.revision == 'HEAD':
      return git.last_commit_hash(self.address, short_hash = True)
    return self.revision
  
check.register_class(git_address)
