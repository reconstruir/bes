#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.text.line_numbers import line_numbers

class test_line_numbers(unit_test):

  def test_fit(self):
    self.assert_string_equal_fuzzy(
      '''\
1|foo
2|bar
3|
''',
      line_numbers.add_line_numbers('foo\nbar\n\n') )
  
if __name__ == '__main__':
  unit_test.main()
