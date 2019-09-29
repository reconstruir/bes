#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.string_util import string_util
from bes.compat.StringIO import StringIO
import copy

class git_status(object):
  'Git status of changes.'

  MODIFIED = 'M'
  ADDED = 'A'
  DELETED = 'D'
  RENAMED = 'R'
  COPIED = 'C'
  UNMERGED = 'U'
  UNTRACKED = '??'

  def __init__(self, action, filename, *args):
    args = args or ()
    self.action = action
    self.filename = filename
    self.args = copy.deepcopy(args)
    
  def __str__(self):
    buf = StringIO()
    buf.write(self.action.rjust(2))
    buf.write(' ')
    buf.write(self.filename)
    for i, arg in enumerate(self.args):
      if i == 0:
        buf.write(' ')
      assert string_util.is_string(arg)
      buf.write(arg)
    return buf.getvalue()

  def __repr__(self):
    return str(self)
  
  def __eq__(self, other):
    if isinstance(other, git_status):
      return self.__dict__ == other.__dict__
    elif isinstance(other, ( tuple, list )):
      return tuple(other) == self.as_tuple()
    else:
      raise TypeError('invalid type for equality comparison: %s - %s' % (str(other), type(other)))

  def as_tuple(self):
    return tuple([ self.action, self.filename ] + list(self.args))
  
  def is_untracked(self):
    return self.action == '??'
  
  @classmethod
  def parse(clazz, s):
    lines = [ line.strip() for line in s.split('\n') ]
    lines = [ line for line in lines if line ]
    return [ clazz.parse_line(line) for line in lines  ]

  @classmethod
  def parse_line(clazz, s):
    v = string_util.split_by_white_space(s)
    action = v[0]
    filename = v[1]
    args = tuple(v[2:0]) or ()
    return clazz(action, filename, *args)
