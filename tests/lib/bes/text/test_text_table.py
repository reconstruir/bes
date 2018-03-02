#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.text import text_table as TT

class test_text_table(unit_test):

  def test_basic(self):
    data = [
      ( 'FRUIT', 'FAVORITE', 'COLOR', 'YUMMINESS', 'CITRUS', 'PRICE' ),
      ( 'kiwi', 'YES', 'green', 5, 5, 2.5 ),
      ( 'banana', '', 'yellow', 2, 1, 1.0 ),
      ( 'blueberry', 'YES', 'purple', 9, 4, 3.0 ),
      ( 'lemon', '', 'yellow', 2, 10, 1.0 ),
    ]
    t = TT(data = data)
    expected = '''\
FRUIT     │ FAVORITE │ COLOR  │ YUMMINESS │ CITRUS │ PRICE │
kiwi      │ YES      │ green  │ 5         │ 5      │ 2.5   │
banana    │          │ yellow │ 2         │ 1      │ 1.0   │
blueberry │ YES      │ purple │ 9         │ 4      │ 3.0   │
lemon     │          │ yellow │ 2         │ 10     │ 1.0   │'''
    self.assertEqual( expected, str(t) )
    
if __name__ == '__main__':
  unit_test.main()
