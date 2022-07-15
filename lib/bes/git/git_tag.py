#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from bes.version.software_version import software_version

class git_tag(namedtuple('git_tag', 'name, commit, commit_short, peeled')):

  def __new__(clazz, name, commit, commit_short, peeled):
    return clazz.__bases__[0].__new__(clazz, name, commit, commit_short, peeled)

  def to_dict(self):
    return dict(self._asdict())
  
check.register_class(git_tag, include_seq = False)
