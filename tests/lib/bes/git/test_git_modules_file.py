#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#
from bes.testing.unit_test import unit_test

#from bes.git.git import git
#from bes.git.git_status import git_status
from bes.git.git_modules_file import git_modules_file
from bes.git.git_modules_file import git_module

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
    mf = git_modules_file.parse_text('<unittest>', text)
    self.assertEqual( [
      ( 'foo', 'foo', 'git@example.com:org/foo.git', None ),
      ( 'bar', 'bar', 'git@example.com:org/bar.git', None ),
    ], mf.modules )
  
  def test_parse_branch(self):
    text = '''\
[submodule "foo"]
	path = foo
	url = git@example.com:org/foo.git
	branch = b1
[submodule "bar"]
	path = bar
	url = git@example.com:org/bar.git
'''
    mf = git_modules_file.parse_text('<unittest>', text)
    self.assertEqual( [
      ( 'foo', 'foo', 'git@example.com:org/foo.git', 'b1' ),
      ( 'bar', 'bar', 'git@example.com:org/bar.git', None ),
    ], mf.modules )
  
  def test___str__(self):
    mods = [
      git_module('foo', 'foo', 'git@example.com:org/foo.git', 'b1'),
      git_module('bar', 'bar', 'git@example.com:org/bar.git', None),
    ]
    mf = git_modules_file('<unittest>', mods)
    expected = '''\
[submodule "foo"]
	path = foo
	url = git@example.com:org/foo.git
	branch = b1
[submodule "bar"]
	path = bar
	url = git@example.com:org/bar.git
'''
    self.assertMultiLineEqual( expected, str(mf) )
  
if __name__ == '__main__':
  unit_test.main()
