#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple
from bes.common import check
from bes.git import git

class file_info(namedtuple('file_info', 'filename,config')):

  def __new__(clazz, config_env, filename):
    if filename is not None:
      check.check_string(filename)
    if not path.isfile(filename):
      raise IOError('File not found: %s' % (filename))
    filename = path.abspath(filename)
    config = config_env.config_for_filename(filename)
    return clazz.__bases__[0].__new__(clazz, filename,config)

  @property
  def git_root(self):
    'Return the git root for this file or None if not within a git repo.'
    if not hasattr(self, '_git_root'):
      setattr(self, '_git_root', self._compute_git_root())
    return getattr(self, '_git_root')

  @property
  def git_tracked(self):
    'Return True if the file is tracked by the git repo.'
    if not hasattr(self, '_git_tracked'):
      setattr(self, '_git_tracked', self._compute_git_tracked())
    return getattr(self, '_git_tracked')

  @property
  def is_broken_link(self):
    return file_util.is_broken_link(self.filename)
  
  def _compute_git_root(self):
    'Compute the git root.'
    try:
      return git.root(self.filename)
    except RuntimeError as ex:
      return None
    except Exception as ex:
      raise
    
  def _compute_git_tracked(self):
    'Compute the git tracked.'
    root = self.git_root
    if not root:
      return False
    return git.is_tracked(root, self.filename)
