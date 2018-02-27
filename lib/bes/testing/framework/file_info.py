#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import exceptions, os.path as path
from collections import namedtuple
from bes.common import check
from bes.fs import file_util
from bes.git import git

from .unit_test_inspect import unit_test_inspect

class file_info(namedtuple('file_info', 'filename,config')):

  def __new__(clazz, config_env, filename):
    if filename is not None:
      check.check_string(filename)
    if not path.isfile(filename):
      raise IOError('File not found: %s' % (filename))
    filename = path.abspath(filename)
    config = config_env.config_for_filename(filename)
    return clazz.__bases__[0].__new__(clazz, filename, config)

  @property
  def relative_filename(self):
    'Return the filename relative to the config root_dir or None if no config was found.'
    if self.config:
      return file_util.remove_head(self.filename, self.config.root_dir)
    else:
      return None

  @property
  def git_root(self):
    'Return the git root for this file or None if not within a git repo.'
    return self._get_or_compute_property('_git_root', self._compute_git_root)

  def _compute_git_root(self):
    'Compute the git root.'
    try:
      return git.root(self.filename)
    except RuntimeError as ex:
      return None
    except Exception as ex:
      raise
    
  @property
  def git_tracked(self):
    'Return True if the file is tracked by the git repo.'
    return self._get_or_compute_property('_git_tracked', self._compute_git_tracked)

  def _compute_git_tracked(self):
    'Compute the git tracked.'
    root = self.git_root
    if not root:
      return False
    return git.is_tracked(root, self.filename)

  @property
  def inspection(self):
    'Return the git root for this file or None if not within a git repo.'
    return self._get_or_compute_property('_inspection', self._compute_inspection)

  def _compute_inspection(self):
    'Compute the git root.'
    try:
      return unit_test_inspect.inspect_file(self.filename)
    except exceptions.SyntaxError, ex:
      #printer.writeln('Failed to inspect: %s - %s' % (f, str(ex)))
      print('1 Failed to inspect: %s - %s' % (self.filename, str(ex)))
      return None
    except Exception, ex:
      #printer.writeln('Failed to inspect: %s - %s:%s' % (f, type(ex), str(ex)))
      print('2 Failed to inspect: %s - %s:%s' % (self.filename, type(ex), str(ex)))
      raise
  
  @property
  def is_broken_link(self):
    return file_util.is_broken_link(self.filename)

  def _get_or_compute_property(self, name, compute_func):
    if not hasattr(self, name):
      setattr(self, name, compute_func())
    return getattr(self, name)
  
check.register_class(file_info, include_seq = False)
