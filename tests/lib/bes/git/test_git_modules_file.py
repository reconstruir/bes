#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#
from bes.testing.unit_test import unit_test

from bes.fs.file_util import file_util
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
    tmp_file = self.make_temp_file(content = text)
    mf = git_modules_file(tmp_file)
    self.assertEqual( [
      ( 'foo', 'foo', 'git@example.com:org/foo.git', None ),
      ( 'bar', 'bar', 'git@example.com:org/bar.git', None ),
    ], mf._modules )
  
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
    tmp_file = self.make_temp_file(content = text)
    mf = git_modules_file(tmp_file)
    self.assertEqual( [
      ( 'foo', 'foo', 'git@example.com:org/foo.git', 'b1' ),
      ( 'bar', 'bar', 'git@example.com:org/bar.git', None ),
    ], mf._modules )
  
  def test___str__(self):
    text = '''\
[submodule "foo"]
	path = foo
	url = git@example.com:org/foo.git
	branch = b1
[submodule "bar"]
	path = bar
	url = git@example.com:org/bar.git
'''
    tmp_file = self.make_temp_file(content = text)
    mf = git_modules_file(tmp_file)
    self.assertMultiLineEqual( text, str(mf) )
  
  def test_set_branch(self):
    text = '''\
[submodule "foo"]
	path = foo
	url = git@example.com:org/foo.git
	branch = b1
[submodule "bar"]
	path = bar
	url = git@example.com:org/bar.git
'''
    tmp_file = self.make_temp_file(content = text)
    mf = git_modules_file(tmp_file)
    mf.set_branch('foo', 'b2')
    expected = '''\
[submodule "foo"]
	path = foo
	url = git@example.com:org/foo.git
	branch = b2
[submodule "bar"]
	path = bar
	url = git@example.com:org/bar.git
'''
    self.assertMultiLineEqual( expected, file_util.read(tmp_file) )
    mf.set_branch('bar', 'b666')
    expected = '''\
[submodule "foo"]
	path = foo
	url = git@example.com:org/foo.git
	branch = b2
[submodule "bar"]
	path = bar
	url = git@example.com:org/bar.git
	branch = b666
'''

  def test_remove_branch(self):
    text = '''\
[submodule "foo"]
	path = foo
	url = git@example.com:org/foo.git
	branch = b2
[submodule "bar"]
	path = bar
	url = git@example.com:org/bar.git
	branch = b666
'''
    tmp_file = self.make_temp_file(content = text)
    mf = git_modules_file(tmp_file)
    mf.set_branch('foo', None)
    mf.set_branch('bar', None)
    expected = '''\
[submodule "foo"]
	path = foo
	url = git@example.com:org/foo.git
[submodule "bar"]
	path = bar
	url = git@example.com:org/bar.git
'''
    self.assertMultiLineEqual( expected, file_util.read(tmp_file) )
    
if __name__ == '__main__':
  unit_test.main()
