#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.warnings.warnings_override import warnings_override
from bes.testing.unit_test import unit_test

class test_warnings_override(unit_test):

  def test_with_no_clause(self):
    with warnings_override(action = 'ignore', category = SyntaxWarning) as _:
      pass

  def test_with_clause(self):
    with warnings_override(clauses = '== 3.8', action = 'ignore', category = SyntaxWarning) as _:
      pass

  def test_with_multiple_clauses(self):
    with warnings_override(clauses = ( '>= 3.8', '<= 3.9' ), action = 'ignore', category = SyntaxWarning) as _:
      pass
    
if __name__ == '__main__':
  unit_test.main()
