#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.text import text_table as TT, text_cell_renderer

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
    self.assertEqual( expected, t.to_string(strip_rows = True) )
    
  def test_cell_style(self):
    self.maxDiff = None
    data = [
      ( 'FRUIT', 'FAVORITE', 'COLOR', 'YUMMINESS', 'CITRUS', 'PRICE' ),
      ( 'kiwi', 'YES', 'green', 5, 5, 2.5 ),
      ( 'banana', '', 'yellow', 2, 1, 1.0 ),
      ( 'blueberry', 'YES', 'purple', 9, 4, 3.0 ),
      ( 'lemon', '', 'yellow', 2, 10, 1.0 ),
    ]
    
    class uppercase_cell_renderer(text_cell_renderer):

      def __init__(self, just = None, width = None):
        super(uppercase_cell_renderer, self).__init__(just = just, width = width)
        
      def render(self, value, width = None):
        upper_value = str(value).upper()
        return super(uppercase_cell_renderer, self).render(upper_value, width = width)
    
    t = TT(data = data)
    t.default_cell_renderer = uppercase_cell_renderer()
    expected = '''\
FRUIT     │ FAVORITE │ COLOR  │ YUMMINESS │ CITRUS │ PRICE │
KIWI      │ YES      │ GREEN  │ 5         │ 5      │ 2.5   │
BANANA    │          │ YELLOW │ 2         │ 1      │ 1.0   │
BLUEBERRY │ YES      │ PURPLE │ 9         │ 4      │ 3.0   │
LEMON     │          │ YELLOW │ 2         │ 10     │ 1.0   │'''
    self.assertMultiLineEqual( expected, t.to_string(strip_rows = True) )

  def xtest_unicode(self):
    data = [
      ( u'mine\u2019s', ),
    ]
    t = TT(data = data)
    print(t)

  def test_blanks(self):
    data = [
      ( 'FRUIT', 'FAVORITE', 'COLOR' ),
      ( 'kiwi', 'YES', 'green' ),
      ( 'banana', '', 'yellow' ),
      ( 'blueberry', 'YES', 'purple' ),
      ( 'lemon', '', 'yellow' ),
    ]
    t = TT(data = data)
    expected = '''\
FRUIT     │ FAVORITE │ COLOR  │
kiwi      │ YES      │ green  │
banana    │          │ yellow │
blueberry │ YES      │ purple │
lemon     │          │ yellow │'''
    self.assertMultiLineEqual( expected, t.to_string(strip_rows = True) )
    
if __name__ == '__main__':
  unit_test.main()
