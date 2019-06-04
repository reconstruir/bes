#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.text.text_table_parser import text_table_parser as TTP
from bes.common.table import table

class test_text_table_parser(unit_test):

  def test_parse_basic(self):
#23456789012
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
    column_widths = ( 12, 11, 9, 12, 9, 8 )
    t = TTP(text, column_widths)
    self.assertEqual( expected, t.table )

  def test_parse_leading_spaces(self):
    self.maxDiff = None
    text = '''
FRUIT       FAVORITE   COLOR    YUMMINESS   CITRUS   PRICE  
 kiwi       YES        green    5           5        2.5    
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
    column_widths = ( 12, 11, 9, 12, 9, 8 )
    t = TTP(text, column_widths)
    self.assertMultiLineEqual( str(expected), str(t.table) )

  def test_parse_column_edges(self):
    self.maxDiff = None
#23456789012
    text = '''
kiwi12345678YES12345678green1234X12345678901Y12345678XYZ12345
'''
    expected = table(data = [
      ( 'kiwi12345678', 'YES12345678', 'green1234', 'X12345678901', 'Y12345678', 'XYZ12345' ),
    ])
    column_widths = ( 12, 11, 9, 12, 9, 8 )
    t = TTP(text, column_widths)
    self.assertMultiLineEqual( str(expected), str(t.table) )
    
  def xtest_parse_uneven_rows(self):
#23456789012
    text = '''
FRUIT       FAVORITE   COLOR    YUMMINESS   CITRUS   PRICE  
kiwi        YES        green    5
banana                 yellow   2           1        1.0    BONUS
blueberry   YES        purple   9           4        3.0    
lemon
'''
    expected = table(data = [
      ( 'FRUIT', 'FAVORITE', 'COLOR', 'YUMMINESS', 'CITRUS', 'PRICE' ),
      ( 'kiwi', 'YES', 'green', '5', None, None ),
      ( 'banana', None, 'yellow', '2', '1', '1.0' ),
      ( 'blueberry', 'YES', 'purple', '9', '4', '3.0' ),
      ( 'lemon', None, None, None, None, None ),
    ])
    column_widths = ( 11, 11, 8, 11, 8, 7 )
    t = TTP(text, column_widths)
    self.assertEqual( expected, t.table )

  def xtest_parse_edges(self):
    text = '''
COL1        COL1       COL3     COL4        COL5     COL6   
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
    
  def test_parse_longer(self):
    self.maxDiff = None
#123456789012345678901234567890123456
    text = '''
 Test Name                          Result                  Flag   Reference Range              Lab
 GLUCOSE                             84                            65-99 mg/dL                  01
 CHOLESTEROL, TOTAL                 200                            125-200 mg/dL                01
'''
    expected = table(data = [
      ( 'kiwi12345678', 'YES12345678', 'green1234', 'X12345678901', 'Y12345678', 'XYZ12345' ),
    ])
    column_widths = (36, 24, 7, 29, 3)
    t = TTP(text, column_widths)
    #self.assertMultiLineEqual( str(expected), str(t.table) )
    print(t)
    
if __name__ == '__main__':
  unit_test.main()
