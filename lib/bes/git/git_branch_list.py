#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, re
from collections import namedtuple

from bes.common import type_checked_list

from .git_branch import git_branch 

class git_branch_list(type_checked_list):

  __value_type__ = git_branch
  
  def __init__(self, values = None):
    super(git_branch_list, self).__init__(values = values)
    
  @property
  def local_names(self):
    return sorted([ b.name for b in self if b.where == 'local' ])
    
  @property
  def remote_names(self):
    return sorted([ b.name for b in self if b.where == 'remote' ])
    
  @property
  def names(self):
    return sorted(list(set(self.local_names + self.remote_names)))

  @property
  def longest_name(self):
    return max([ len(name) for name in self.names ])

  @property
  def comments(self):
    return sorted(list(set([ b.comment for b in self ])))

  @property
  def longest_comment(self):
    return max([ len(comment) for comment in self.comments ])

  @property
  def difference(self):
    'Return remote branches not local.'
    remote_set = set(self.remote_names)
    local_set = set(self.local_names)
    return sorted(list(remote_set - local_set))

  def has_local(self, name):
    return name in self.local_names

  def has_remote(self, name):
    return name in self.remote_names

  def mutated_values(self, mutations):
    return git_branch_list([ v.clone(mutations) for v in self ])
    
  def find_by_name(self, name):
    for b in self:
      if b.name == name:
        return b
    return None
