#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#
from bes.testing.unit_test import unit_test
from bes.git.git_tag_list import git_tag_list
from bes.git.git_unit_test import git_temp_home_func

class test_git_tag_list(unit_test):

  @git_temp_home_func()
  def test__parse_show_ref_one_line(self):
    self.assertEqual(
      ( '1.0.0', '18a911e5fd469294352004178190f49e59d936f9', '18a911e', False ),
    git_tag_list._parse_show_ref_one_line('18a911e5fd469294352004178190f49e59d936f9    refs/tags/1.0.0') )

  @git_temp_home_func()
  def test__parse_show_ref_one_line_peeled(self):
    self.assertEqual(
      ( '1.0.0', '18a911e5fd469294352004178190f49e59d936f9', '18a911e', True ),
    git_tag_list._parse_show_ref_one_line('18a911e5fd469294352004178190f49e59d936f9    refs/tags/1.0.0^{}') )
    
  @git_temp_home_func()
  def test_parse_show_ref_output(self):
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
    ], git_tag_list.parse_show_ref_output(output) )
    
  @git_temp_home_func()
  def test_parse_show_ref_output_peeled(self):
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
    ], git_tag_list.parse_show_ref_output(output) )

  @git_temp_home_func()
  def test_parse_show_ref_output_lexical_sort(self):
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
      ( '1.0.10', '03001234567890abcdef1234567890abcdef1234', '0300123', False ),
      ( '1.0.100', '04001234567890abcdef1234567890abcdef1234', '0400123', False ),
      ( '1.0.2', '05001234567890abcdef1234567890abcdef1234', '0500123', False ),
    ], git_tag_list.parse_show_ref_output(output, sort_type = 'lexical') )

  @git_temp_home_func()
  def test_parse_show_ref_output_reverse(self):
    output = '''\
01001234567890abcdef1234567890abcdef1234    refs/tags/1.0.0
02001234567890abcdef1234567890abcdef1234    refs/tags/1.0.1
03001234567890abcdef1234567890abcdef1234    refs/tags/1.0.10
04001234567890abcdef1234567890abcdef1234    refs/tags/1.0.100
05001234567890abcdef1234567890abcdef1234	  refs/tags/1.0.2
'''
    self.assertEqual( [
      ( '1.0.100', '04001234567890abcdef1234567890abcdef1234', '0400123', False ),
      ( '1.0.10', '03001234567890abcdef1234567890abcdef1234', '0300123', False ),
      ( '1.0.2', '05001234567890abcdef1234567890abcdef1234', '0500123', False ),
      ( '1.0.1', '02001234567890abcdef1234567890abcdef1234', '0200123', False ),
      ( '1.0.0', '01001234567890abcdef1234567890abcdef1234', '0100123', False ),
    ], git_tag_list.parse_show_ref_output(output, reverse = True) )
    
if __name__ == '__main__':
  unit_test.main()
