#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.text.text_table import text_table as TT
from bes.text.text_table import text_cell_renderer
from bes.text.text_table import text_table_style
from bes.text.text_box import text_box_ascii

class test_text_table(unit_test):

  _STYLE = text_table_style(spacing = 1, box = text_box_ascii())
  
  def test_basic(self):
    data = [
      ( 'FRUIT', 'FAVORITE', 'COLOR', 'YUMMINESS', 'CITRUS', 'PRICE' ),
      ( 'kiwi', 'YES', 'green', 5, 5, 2.5 ),
      ( 'banana', '', 'yellow', 2, 1, 1.0 ),
      ( 'blueberry', 'YES', 'purple', 9, 4, 3.0 ),
      ( 'lemon', '', 'yellow', 2, 10, 1.0 ),
    ]
    t = self._make_text_table(data)
    expected = '''\
+------------------------------------------------------------+
| FRUIT     | FAVORITE | COLOR  | YUMMINESS | CITRUS | PRICE |
| kiwi      | YES      | green  | 5         | 5      | 2.5   |
| banana    |          | yellow | 2         | 1      | 1.0   |
| blueberry | YES      | purple | 9         | 4      | 3.0   |
| lemon     |          | yellow | 2         | 10     | 1.0   |
+------------------------------------------------------------+'''
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
    
    t = self._make_text_table(data)
    t.default_cell_renderer = uppercase_cell_renderer()
    expected = '''\
+------------------------------------------------------------+
| FRUIT     | FAVORITE | COLOR  | YUMMINESS | CITRUS | PRICE |
| KIWI      | YES      | GREEN  | 5         | 5      | 2.5   |
| BANANA    |          | YELLOW | 2         | 1      | 1.0   |
| BLUEBERRY | YES      | PURPLE | 9         | 4      | 3.0   |
| LEMON     |          | YELLOW | 2         | 10     | 1.0   |
+------------------------------------------------------------+'''
    self.assertMultiLineEqual( expected, t.to_string(strip_rows = True) )

  def xtest_unicode(self):
    data = [
      ( u'mine\u2019s', ),
    ]
    t = self._make_text_table(data)
    print(t)

  def test_blanks(self):
    data = [
      ( 'FRUIT', 'FAVORITE', 'COLOR' ),
      ( 'kiwi', 'YES', 'green' ),
      ( 'banana', '', 'yellow' ),
      ( 'blueberry', 'YES', 'purple' ),
      ( 'lemon', '', 'yellow' ),
    ]
    t = self._make_text_table(data)
    expected = '''\
+-------------------------------+
| FRUIT     | FAVORITE | COLOR  |
| kiwi      | YES      | green  |
| banana    |          | yellow |
| blueberry | YES      | purple |
| lemon     |          | yellow |
+-------------------------------+'''
    self.assertMultiLineEqual( expected, t.to_string(strip_rows = True) )

  def test_sort_by_column(self):
    data = [
      ( 'FRUIT', 'FAVORITE', 'COLOR' ),
      ( 'kiwi', 'YES', 'green' ),
      ( 'banana', 'NO', 'yellow' ),
      ( 'blueberry', 'YES', 'purple' ),
      ( 'lemon', 'NO', 'yellow' ),
    ]
    t = self._make_text_table(data)
    t.sort_by_column(0)
    expected = '''\
+-------------------------------+
| FRUIT     | FAVORITE | COLOR  |
| banana    | NO       | yellow |
| blueberry | YES      | purple |
| kiwi      | YES      | green  |
| lemon     | NO       | yellow |
+-------------------------------+'''
    self.assertMultiLineEqual( expected, t.to_string(strip_rows = True) )

    t.sort_by_column(1)
    expected = '''\
+-------------------------------+
| FRUIT     | FAVORITE | COLOR  |
| banana    | NO       | yellow |
| lemon     | NO       | yellow |
| blueberry | YES      | purple |
| kiwi      | YES      | green  |
+-------------------------------+'''
    self.assertMultiLineEqual( expected, t.to_string(strip_rows = True) )

    t.sort_by_column(2)
    expected = '''\
+-------------------------------+
| FRUIT     | FAVORITE | COLOR  |
| kiwi      | YES      | green  |
| blueberry | YES      | purple |
| banana    | NO       | yellow |
| lemon     | NO       | yellow |
+-------------------------------+'''
    self.assertMultiLineEqual( expected, t.to_string(strip_rows = True) )
    
  def test_sort_by_column_named(self):
    data = [
      ( 'kiwi', 'YES', 'green' ),
      ( 'banana', 'NO', 'yellow' ),
      ( 'blueberry', 'YES', 'purple' ),
      ( 'lemon', 'NO', 'yellow' ),
    ]
    t = self._make_text_table(data)
    t.set_labels( ( 'FRUIT', 'FAVORITE', 'COLOR' ) )
    t.sort_by_column('FRUIT')
    expected = '''\
|-------------------------------|
| FRUIT     | FAVORITE | COLOR  |
+-------------------------------+
| banana    | NO       | yellow |
| blueberry | YES      | purple |
| kiwi      | YES      | green  |
| lemon     | NO       | yellow |
+-------------------------------+'''
    self.assertMultiLineEqual( expected, t.to_string(strip_rows = True) )
    t.sort_by_column('FAVORITE')
    expected = '''\
|-------------------------------|
| FRUIT     | FAVORITE | COLOR  |
+-------------------------------+
| banana    | NO       | yellow |
| lemon     | NO       | yellow |
| blueberry | YES      | purple |
| kiwi      | YES      | green  |
+-------------------------------+'''
    self.assertMultiLineEqual( expected, t.to_string(strip_rows = True) )

    t.sort_by_column('COLOR')
    expected = '''\
|-------------------------------|
| FRUIT     | FAVORITE | COLOR  |
+-------------------------------+
| kiwi      | YES      | green  |
| blueberry | YES      | purple |
| banana    | NO       | yellow |
| lemon     | NO       | yellow |
+-------------------------------+'''
    self.assertMultiLineEqual( expected, t.to_string(strip_rows = True) )
    
  def _make_text_table(self, data):
    return TT(data = data, style = self._STYLE)

  
if __name__ == '__main__':
  unit_test.main()
