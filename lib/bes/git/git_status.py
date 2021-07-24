#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy

from bes.common.check import check
from bes.common.string_util import string_util
from bes.common.type_checked_list import type_checked_list
from bes.compat.StringIO import StringIO
from bes.text.text_line_parser import text_line_parser

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
  def parse_line(clazz, s):
    check.check_string(s)
    
    v = string_util.split_by_white_space(s)
    action = v[0]
    filename = v[1]
    args = tuple(v[2:0]) or ()
    return git_status(action, filename, *args)

  def __eq__(self, other):
    if check.is_string(other):
      other = self.parse_line(other)
    elif check.is_git_status(other):
      other = other.as_tuple()
    return self.as_tuple() == other

  def __gt__(self, other):
    if check.is_string(other):
      other = parse_line(other)
    return self.as_tuple() > other.as_tuple()
  
check.register_class(git_status, include_seq = False)

class git_status_list(type_checked_list):

  __value_type__ = git_status
  
  def __init__(self, values = None):
    super(git_status_list, self).__init__(values = values)

  @classmethod  
  def parse(clazz, text):
    check.check_string(text)
    
    lines = text_line_parser.parse_lines(text, strip_comments = False, strip_text = True, remove_empties = True)
    return git_status_list([ git_status.parse_line(line) for line in lines  ])
    
check.register_class(git_status_list, include_seq = False)
