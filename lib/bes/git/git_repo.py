#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from .git import git
from .git_util import git_util

class git_repo(object):
  'A mini git repo abstraction.'

  def __init__(self, root_dir, address):
    self.address = address
    self.root_dir = path.join(root_dir, git_util.sanitize_address(address))
    
  def update(self):
    git.clone_or_update(self.address, self.root_dir)

  def exists(self):
    return path.isdir(self._dot_git_path())

  def branch_status(self):
    return git.branch_status(self.root_dir)

  def _dot_git_path(self):
    return path.join(self.root_dir, '.git')
