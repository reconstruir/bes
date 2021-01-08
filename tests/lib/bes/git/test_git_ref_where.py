#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#

from bes.testing.unit_test import unit_test
from bes.git.git_ref_where import git_ref_where

class test_git_ref_where(unit_test):

  def test_has_determine_where(self):
    self.assertEqual( 'both', git_ref_where.determine_where(True, True) )
    self.assertEqual( 'local', git_ref_where.determine_where(True, False) )
    self.assertEqual( 'remote', git_ref_where.determine_where(False, True) )
    self.assertEqual( 'both', git_ref_where.determine_where(None, None) )
    
if __name__ == '__main__':
  unit_test.main()
