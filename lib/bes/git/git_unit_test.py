#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from functools import wraps
import os
import os.path as path

from bes.fs.file_util import file_util
from bes.testing.unit_test import unit_test
from bes.system.env_override import env_override

from .git import git

class git_unit_test(object):
  'Class to help write unit tests that use git.'

  @classmethod
  def set_identity(clazz):
    if not path.exists(path.expanduser(clazz.gitconfig_filename())):
      git.config_set_identity('Unit Test', 'unittest@example.com')
      setattr(clazz, '_did_set_git_identity', True)

  @classmethod
  def unset_identity(clazz):
    if getattr(clazz, '_did_set_git_identity', False):
      file_util.remove(clazz.gitconfig_filename())

  @classmethod
  def gitconfig_filename(clazz):
    # Dont use path.expanduser() because starting with python 3.8 on windows
    # it no longer uses the value of %HOME%
    return path.join(os.environ.get('HOME'), '.gitconfig')
      
def git_temp_home_func():
  'A decorator to override HOME for a function.'
  def _wrap(func):
    @wraps(func)
    def _caller(self, *args, **kwargs):
      with env_override.temp_home() as env:
        git_unit_test.set_identity()
        return func(self, *args, **kwargs)
    return _caller
  return _wrap
      
