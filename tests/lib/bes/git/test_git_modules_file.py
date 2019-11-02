#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#
import os.path as path, os, unittest

from bes.testing.unit_test import unit_test
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.archive.archiver import archiver
from bes.git.git_unit_test import git_temp_home_func
from bes.system.env_override import env_override_temp_home_func

#from bes.git.git import git
#from bes.git.git_status import git_status
from bes.git.git_modules_file import git_modules_file

class test_git_submodules_file(unit_test):

  def test_parse_text(self):
    text = '''\
[submodule "foo"]
	path = foo
	url = git@example.com:org/foo.git
[submodule "bar"]
	path = bar
	url = git@example.com:org/bar.git
'''
    m = git_modules_file.parse_text('<unittest>', text)
    self.assertEqual( [
      ( 'foo', 'foo', 'git@example.com:org/foo.git', None ),
      ( 'bar', 'bar', 'git@example.com:org/bar.git', None ),
    ], m.modules )
  
if __name__ == '__main__':
  unit_test.main()
