#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs import temp_file
from bes.fs.testing import temp_content

from .git import git
from .git_util import git_util

class repo(object):
  'A mini git repo abstraction.'

  def __init__(self, root, address = None):
    self.root = path.abspath(root)
    self.address = address
    
  def clone_or_pull(self):
    return git.clone_or_pull(self.address, self.root)

  def init(self):
    return git.init(self.root)

  def add(self, filenames):
    return git.add(self.root, filenames)

  def pull(self):
    return git.pull(self.root)

  def commit(self, message, filenames):
    return git.commit(self.root, message, filenames)
    
  def status(self, filenames):
    return git.status(self.root, filenames)
    
  def exists(self):
    return path.isdir(self._dot_git_path())

  def branch_status(self):
    return git.branch_status(self.root)

  def write_temp_content(self, items):
    temp_content.write_items(items, self.root)

  def _dot_git_path(self):
    return path.join(self.root, '.git')

  @classmethod
  def make_temp_repo(clazz, address = None, content = None):
    tmp_dir = temp_file.make_temp_dir()
    r = repo(tmp_dir, address = address)
    r.init()
    if content:
      r.write_temp_content(content)
      r.add('.')
      r.commit('add temp content', '.')
    return r
  
