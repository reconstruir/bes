#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.git.git_ref_info import git_ref_info
from bes.git.git_error import git_error

class test_git_ref_info(unit_test):

  def test_parse_show_ref_output_tag(self):
    f = git_ref_info.parse_show_ref_output

    output = '''\
deadbeefdeadbeefdeadbeefdeadbeefdeadbeef refs/tags/1.2.3
'''
    self.assertEqual( ( '1.2.3', 'refs/tags/1.2.3', 'tag', 'deadbeefdeadbeefdeadbeefdeadbeefdeadbeef', 'deadbee', False),
                      f(output) )

  def test_parse_show_ref_output_branch(self):
    f = git_ref_info.parse_show_ref_output

    output = '''\
deadbeefdeadbeefdeadbeefdeadbeefdeadbeef refs/heads/master
'''
    self.assertEqual( ( 'master', 'refs/heads/master', 'branch', 'deadbeefdeadbeefdeadbeefdeadbeefdeadbeef', 'deadbee', False),
                      f(output) )
    
  def test_parse_show_ref_output_branch_with_remote(self):
    f = git_ref_info.parse_show_ref_output

    output = '''\
deadbeefdeadbeefdeadbeefdeadbeefdeadbeef refs/heads/master
deadbeefdeadbeefdeadbeefdeadbeefdeadbeef refs/remotes/origin/master
'''
    self.assertEqual( ( 'master', 'refs/heads/master', 'branch', 'deadbeefdeadbeefdeadbeefdeadbeefdeadbeef', 'deadbee', True),
                      f(output) )
    
  def test_parse_show_ref_output_tag_that_is_also_branch(self):
    f = git_ref_info.parse_show_ref_output

    output = '''\
deadbeefdeadbeefdeadbeefdeadbeefdeadbeef refs/tags/master
deadbeefdeadbeefdeadbeefdeadbeefdeadbeef refs/heads/master
deadbeefdeadbeefdeadbeefdeadbeefdeadbeef refs/remotes/origin/master
'''
    with self.assertRaises(git_error) as ctx:
      f(output)
      self.assertTrue( 'Ref that is both a branch and tag is not supported' in str(ctx.exception) )
    
  def test_parse_show_ref_output_only_heads(self):
    f = git_ref_info.parse_show_ref_output

    output = '''\
deadbeefdeadbeefdeadbeefdeadbeefdeadbeef refs/heads/test1
'''
    self.assertEqual( ( 'test1', 'refs/heads/test1', 'branch', 'deadbeefdeadbeefdeadbeefdeadbeefdeadbeef', 'deadbee', False),
                      f(output) )

  def test_parse_show_ref_output_only_remotes(self):
    f = git_ref_info.parse_show_ref_output

    output = '''\
deadbeefdeadbeefdeadbeefdeadbeefdeadbeef refs/remotes/origin/test1
'''
    self.assertEqual( ( 'test1', 'refs/remotes/origin/test1', 'branch', 'deadbeefdeadbeefdeadbeefdeadbeefdeadbeef', 'deadbee', True),
                      f(output) )
    
if __name__ == '__main__':
  unit_test.main()
