#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from os import path

from bes.fs.file_util import file_util
from bes.testing.unit_test import unit_test

from .git import git

class git_unit_test(object):
  'Class to help write unit tests that use git.'

  @classmethod
  def set_identity(clazz):
    if not path.exists(path.expanduser('~/.gitconfig')):
      git.config_set_identity('Unit Test', 'unittest@example.com')
      setattr(clazz, '_did_set_git_identity', True)

  @classmethod
  def unset_identity(clazz):
    if getattr(clazz, '_did_set_git_identity', False):
      file_util.remove(path.expanduser('~/.gitconfig'))
