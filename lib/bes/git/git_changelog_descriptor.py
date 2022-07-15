# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check

class changelog_descriptor(namedtuple('changelog_descriptor', 'root_dir, from_revision, to_revision')):
  'A class to describe a git changelog.'
  
  def __new__(clazz, root_dir, from_revision, to_revision):
    check.check_string(root_dir)
    check.check_string(from_revision)
    check.check_string(to_revision)

    return clazz.__bases__[0].__new__(clazz, root_dir, from_revision, to_revision)

  def to_dict(self):
    return dict(self._asdict())
  
check.register_class(changelog_descriptor, include_seq = True)
