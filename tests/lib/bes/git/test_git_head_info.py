#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.git.git_head_info import git_head_info

class test_git_remote(unit_test):

  def test_parse_head_info(self):
    f = git_head_info.parse_head_info
    self.assertEqual( ( 'release-beta-14-studio-fixes', None, '9038154f', 'track branch release-beta-14-studio-fixes [skip ci]', False ),
                      f('* release-beta-14-studio-fixes 9038154f track branch release-beta-14-studio-fixes [skip ci]') )
    self.assertEqual( ( 'b1', None, 'b59bc43', 'message 1', False ),
                      f('* b1     b59bc43 message 1') )

if __name__ == '__main__':
  unit_test.main()
