#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.text import text_line, line_continuation_merger as M

class test_line_continuation_merger(unit_test):

  def test_empty(self):
    self.assertEqual( [],
                      self._merge(r'') )

  def test_no_continuation(self):
    text=r'''foo
bar'''
    self.assertEqual( [
      ( 1, 'foo'),
      ( 2, 'bar'),
    ], self._merge(text) )
    
  def test_complete(self):
    text=r'''foo bar
pear \
kiwi
apple \
pineapple
almond \
walnut \
peanut \
pecan'''
    self.assertEqual( [
      ( 1, 'foo bar'),
      ( 2, 'pear kiwi'),
      ( 3, ''),
      ( 4, 'apple pineapple'),
      ( 5, ''),
      ( 6, 'almond walnut peanut pecan'),
      ( 7, ''),
      ( 8, ''),
      ( 9, ''),
    ], self._merge(text) )
    
  def test_one_continuation(self):
    text=r'''pear \
kiwi'''
    self.assertEqual( [
      ( 1, 'pear kiwi'),
      ( 2, ''),
    ], self._merge(text) )
    
  @classmethod
  def _merge(self, text):
    if not text:
      return []
    lines = text.split('\n')
    lines = [ text_line(*item) for item in zip(range(1, len(lines) + 1), lines) ]
    for x in lines:
      print(' IN: "%s"' % (str(x)))
    return M.merge_to_list(lines)

  def assertEqual(self, expected, actual):
    assert isinstance(expected, list)
    expected = [ text_line(*t) for t in expected ]
    super(test_line_continuation_merger, self).assertEqual(expected, actual)

if __name__ == '__main__':
  unit_test.main()
