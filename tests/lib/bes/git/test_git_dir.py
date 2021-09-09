#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys
import os.path as path

from bes.fs.file_util import file_util
from bes.git.git_error import git_error
from bes.git.git_repo import git_repo
from bes.git.git_temp_repo import git_temp_repo
from bes.git.git_unit_test import git_temp_home_func
from bes.system.env_override import env_override_temp_home_func
from bes.testing.unit_test import unit_test
from bes.git.git_dir import git_dir
from bes.git.git_repo_status_options import git_repo_status_options

class test_git_dir(unit_test):

  @git_temp_home_func()
  def find_git_dirs(self):
    tmp_dir = self.make_temp_dir()
    
if __name__ == '__main__':
  unit_test.main()
