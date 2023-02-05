#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.common.binary_searcher import binary_searcher
from bes.system.log import logger

class test_binary_searcher(unit_test):

  def test_search(self):

    _log = logger('binary_searcher')
    
    class _searcher(binary_searcher):

      def __init__(self, array):
        self._array = array

      def item_at_index(self, index):
        self._log.log_d(f'_searcher.item_at_index({index})')
        return self._array[index]

      def compare(self, item1, item2):
        if item1 == item2:
          rv = 0
        elif item1 < item2:
          rv = -1
        else:
          rv = 1
        self._log.log_d(f'_searcher.compare({item1}, {item2}) => {rv}')
        return rv

      def low_index(self):
        return 0

      def high_index(self):
        return len(self._array) - 1

    l = [ 3, 42, 45, 55, 67, 90, 97, 101, 666, 999, 1001, 9999 ]
    self.assertEqual( True, l == sorted(l) )
    self.assertEqual( True, (len(l) % 2) == 0 )
    s = _searcher(l)
    self.assertEqual( None, s.search(4545) )
    self.assertEqual( 0, s.search(3) )
    self.assertEqual( 1, s.search(42) )
    self.assertEqual( 2, s.search(45) )
    self.assertEqual( 3, s.search(55) )
    self.assertEqual( 4, s.search(67) )
    self.assertEqual( 5, s.search(90) )
    self.assertEqual( 6, s.search(97) )
    self.assertEqual( 7, s.search(101) )
    self.assertEqual( 8, s.search(666) )
    self.assertEqual( 9, s.search(999) )
    self.assertEqual( 10, s.search(1001) )
#    self.assertEqual( 11, s.search(9999) )
    
if __name__ == '__main__':
  unit_test.main()
