# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from bes.common.string_util import string_util

from .git_error import git_error

class git_lfs_entry(namedtuple('git_lfs_entry', 'filename, oid, is_pointer')):
  'A class to deal with git lfs entries.'

  def __new__(clazz, filename, oid, is_pointer):
    check.check_string(filename)
    check.check_string(oid)
    check.check_bool(is_pointer)

    if len(oid) != 64:
      raise git_error('oid should be exactly 64 chars long: {}'.format(oid))
    
    return clazz.__bases__[0].__new__(clazz, filename, oid, is_pointer)

  def __str__(self):
    ss = '-' if self.is_pointer else '*'
    return '{} {} {}'.format(self.oid, ss, self.filename)

  @property
  def oid_short(self):
    'Return the short object id'
    return self.oid[0:10]
        
  @classmethod
  def parse_entry(clazz, text):
    check.check_string(text)

    parts = string_util.split_by_white_space(text, strip = True)
    if len(parts) < 3:
      raise git_error('Invalid git lfs entry.  Should have 3 parts: "{}"'.format(text))
    oid = parts.pop(0)
    is_pointer_flag = parts.pop(0)
    is_pointer = is_pointer_flag == '-'
    head = oid + ' ' + is_pointer_flag + ' '
    filename = string_util.remove_head(text, head)
    return git_lfs_entry(filename, oid, is_pointer)
