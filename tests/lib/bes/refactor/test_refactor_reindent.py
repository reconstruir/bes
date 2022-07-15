#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.refactor.refactor_reindent import refactor_reindent
from bes.testing.unit_test import unit_test

class test_refactor_reindent(unit_test):

  def test_reindent(self):
    content = '''\
def foo(x):
    if x == None:
        return None
    y = 666
    return x + y
'''

    tmp = self.make_temp_file(content = content, suffix = '.py')
    refactor_reindent.reindent_file(tmp, 2, False)
    expected = '''\
def foo(x):
  if x == None:
    return None
  y = 666
  return x + y
'''
    self.assert_text_file_equal_fuzzy( expected, tmp )
    refactor_reindent.reindent_file(tmp, 8, False)
    expected = '''\
def foo(x):
        if x == None:
                return None
        y = 666
        return x + y
'''
    self.assert_text_file_equal_fuzzy( expected, tmp )
    
if __name__ == '__main__':
  unit_test.main()
