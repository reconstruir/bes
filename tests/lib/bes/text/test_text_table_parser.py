#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.text import text_table_parser as TTP
from bes.common import table

class test_text_table_parser(unit_test):

  def test_parse(self):
    text = '''
FRUIT       FAVORITE   COLOR    YUMMINESS   CITRUS   PRICE  
kiwi        YES        green    5           5        2.5    
banana                 yellow   2           1        1.0    
blueberry   YES        purple   9           4        3.0    
lemon                  yellow   2           10       1.0
'''
    expected = table(data = [
      ( 'FRUIT', 'FAVORITE', 'COLOR', 'YUMMINESS', 'CITRUS', 'PRICE' ),
      ( 'kiwi', 'YES', 'green', '5', '5', '2.5' ),
      ( 'banana', None, 'yellow', '2', '1', '1.0' ),
      ( 'blueberry', 'YES', 'purple', '9', '4', '3.0' ),
      ( 'lemon', None, 'yellow', '2', '10', '1.0' ),
    ])
    column_widths = ( 12, 10, 8, 12, 9, 7 )
    t = TTP(text, column_widths)
    self.assertEqual( expected, t.table )
    
if __name__ == '__main__':
  unit_test.main()
