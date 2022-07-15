#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from os import path

from ..system.check import check
from bes.common.string_util import string_util
from bes.common.tuple_util import tuple_util
from bes.common.type_checked_list import type_checked_list
from bes.compat.StringIO import StringIO
from bes.text.text_line_parser import text_line_parser

from .git_status_action import git_status_action

class git_status(namedtuple('git_status', 'action, filename, renamed_filename')):

  def __new__(clazz, action, filename, renamed_filename):
    check.check_git_status_action(action)
    check.check_string(filename)
    check.check_string(renamed_filename, allow_none = True)
    
    return clazz.__bases__[0].__new__(clazz, action, filename, renamed_filename)

  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)

  def clone_with_abs_filename(self, root_dir):
    check.check_string(root_dir)

    return self.clone(mutations = { 'filename': path.join(root_dir, self.filename) })
  
  def __str__(self):
    buf = StringIO()
    buf.write(self.action.value.rjust(2))
    buf.write(' ')
    buf.write(self.filename)
    if self.renamed_filename:
      buf.write(' -> ')
      buf.write(self.renamed_filename)
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
    return tuple([ self.action, self.filename, self.renamed_filename ])
  
  def is_untracked(self):
    return self.action == git_status_action.UNTRACKED

  @classmethod
  def parse_line(clazz, s):
    check.check_string(s)
    
    v = string_util.split_by_white_space(s)
    #print(f'v={v}')
    action = git_status_action.parse(v.pop(0))
    filename = v.pop(0)
    renamed_filename = None
    if v:
      arrow = v.pop(0)
      if arrow == '->':
        assert len(v) > 0
        renamed_filename = v.pop(0)
    return git_status(action, filename, renamed_filename)

  def __eq__(self, other):
    if check.is_string(other):
      other = self.parse_line(other)
    elif check.is_git_status(other):
      other = other.as_tuple()
    return self.as_tuple() == other

  def __gt__(self, other):
    if check.is_string(other):
      other = self.parse_line(other)
    elif check.is_git_status(other):
      other = other.as_tuple()
    return self.as_tuple() > other
  
check.register_class(git_status, include_seq = False)

class git_status_list(type_checked_list):

  __value_type__ = git_status
  
  def __init__(self, values = None):
    super(git_status_list, self).__init__(values = values)

  def remove_untracked(self):
    self._values = [ v for v in self._values if not v.is_untracked() ]
    
  @classmethod  
  def parse(clazz, text):
    check.check_string(text)
    
    lines = text_line_parser.parse_lines(text, strip_comments = False, strip_text = True, remove_empties = True)
    return git_status_list([ git_status.parse_line(line) for line in lines  ])

  def become_absolute(self, root_dir):
    'Change all the item paths to be absolute starting at root_dir'
    check.check_string(root_dir)

    self._values = [ item.clone_with_abs_filename(root_dir) for item in self ]
  
check.register_class(git_status_list, include_seq = False)
