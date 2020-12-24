#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#
from bes.testing.unit_test import unit_test
from bes.git.git_tag import git_tag as git_tag
from bes.git.git_unit_test import git_temp_home_func

class test_git_tag(unit_test):

  @git_temp_home_func()
  def test__parse_remote_tag_line(self):
    self.assertEqual(
      ( '1.0.0', '18a911e5fd469294352004178190f49e59d936f9', '18a911e', False ),
    git_tag._parse_remote_tag_line('18a911e5fd469294352004178190f49e59d936f9    refs/tags/1.0.0') )

  @git_temp_home_func()
  def test__parse_remote_tag_line_peeled(self):
    self.assertEqual(
      ( '1.0.0', '18a911e5fd469294352004178190f49e59d936f9', '18a911e', True ),
    git_tag._parse_remote_tag_line('18a911e5fd469294352004178190f49e59d936f9    refs/tags/1.0.0^{}') )
    
  @git_temp_home_func()
  def test_parse_remote_tags(self):
    output = '''\
01001234567890abcdef1234567890abcdef1234    refs/tags/1.0.0
02001234567890abcdef1234567890abcdef1234    refs/tags/1.0.1
03001234567890abcdef1234567890abcdef1234    refs/tags/1.0.10
04001234567890abcdef1234567890abcdef1234    refs/tags/1.0.100
05001234567890abcdef1234567890abcdef1234	  refs/tags/1.0.2
'''
    self.assertEqual( [
      ( '1.0.0', '01001234567890abcdef1234567890abcdef1234', '0100123', False ),
      ( '1.0.1', '02001234567890abcdef1234567890abcdef1234', '0200123', False ),
      ( '1.0.2', '05001234567890abcdef1234567890abcdef1234', '0500123', False ),
      ( '1.0.10', '03001234567890abcdef1234567890abcdef1234', '0300123', False ),
      ( '1.0.100', '04001234567890abcdef1234567890abcdef1234', '0400123', False ),
    ], git_tag.parse_remote_tags(output) )
    
  @git_temp_home_func()
  def test_parse_remote_tags_peeled(self):
    output = '''\
01001234567890abcdef1234567890abcdef1234    refs/tags/1.0.0
02001234567890abcdef1234567890abcdef1234    refs/tags/1.0.1^{}
03001234567890abcdef1234567890abcdef1234    refs/tags/1.0.10
04001234567890abcdef1234567890abcdef1234    refs/tags/1.0.100^{}
05001234567890abcdef1234567890abcdef1234	  refs/tags/1.0.2
'''
    self.assertEqual( [
      ( '1.0.0', '01001234567890abcdef1234567890abcdef1234', '0100123', False ),
      ( '1.0.1', '02001234567890abcdef1234567890abcdef1234', '0200123', True ),
      ( '1.0.2', '05001234567890abcdef1234567890abcdef1234', '0500123', False ),
      ( '1.0.10', '03001234567890abcdef1234567890abcdef1234', '0300123', False ),
      ( '1.0.100', '04001234567890abcdef1234567890abcdef1234', '0400123', True ),
    ], git_tag.parse_remote_tags(output) )
    
if __name__ == '__main__':
  unit_test.main()
