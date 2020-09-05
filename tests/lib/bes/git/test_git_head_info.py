#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.git.git_head_info import git_head_info

class test_git_head_info(unit_test):

  def test_parse_head_info(self):
    f = git_head_info.parse_head_info
    self.assertEqual( ( 'branch', 'release-beta-14-studio-fixes', None, '9038154f', 'track branch release-beta-14-studio-fixes [skip ci]', None ),
                      f(None, '* release-beta-14-studio-fixes 9038154f track branch release-beta-14-studio-fixes [skip ci]') )
    self.assertEqual( ( 'branch', 'b1', None, 'b59bc43', 'message 1', None ),
                      f(None, '* b1     b59bc43 message 1') )

  def test_parse_head_info_master(self):
    f = git_head_info.parse_head_info
    self.assertEqual( ( 'branch', 'master', None, 'deadbeef', 'fix foo.', None ),
                      f(None, '* master          deadbeef fix foo.') )

  def test_match_ref_branches(self):
    h = git_head_info('tag', None, 'builds/foo/1.2.3', 'deadbeef', 'foo', [ 'master', 'release-beta-26', 'release-beta-27' ])
    self.assertEqual( [ 'release-beta-26', 'release-beta-27' ], h.match_ref_branches([ 'release-beta-*' ]) )

  def test_parse_head_info_detached_tag(self):
    output = '''\
* (HEAD detached at 1.2.3) deadbeef fixed stuff
  foo
  master
  zoo
'''
    self.assertEqual( ( 'tag', None, '1.2.3', 'deadbeef', 'fixed stuff', None ),
                      git_head_info.parse_head_info(None, output) )
    
  def test_parse_head_info_detached_commit(self):
    output = '''\
* (HEAD detached at deadbeef) deadbeef fixed stuff
  foo
  master
  zoo
'''
    self.assertEqual( ( 'detached_commit', None, None, 'deadbeef', 'fixed stuff', None ),
                      git_head_info.parse_head_info(None, output) )
    
if __name__ == '__main__':
  unit_test.main()
