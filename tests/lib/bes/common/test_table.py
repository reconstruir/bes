#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.common import table

class test_table(unit_test):

  def test___init__empty(self):
    t = table()
    self.assertEqual( 0, t.width )
    self.assertEqual( 0, t.height )

  def test___init__empty_with_width(self):
    t = table()
    t.append_row( ( 'cherry', 'red' ) )
    self.assertEqual( 2, t.width )
    self.assertEqual( 1, t.height )
    t.append_row( ( 'lemon', 'yellow' ) )
    self.assertEqual( 2, t.width )
    self.assertEqual( 2, t.height )

  def test___init__with_data(self):
    t =  table(data = [
      ( 1, 2 ),
      ( 3, 4 ),
    ])
    self.assertEqual( 2, t.width )
    self.assertEqual( 2, t.height )
    
  def test___init__with_table_data(self):
    t1 = table(data = [
      ( 1, 2 ),
      ( 3, 4 ),
    ])
    t2 =  table(data = t1)
    self.assertEqual( ( 1, 2 ), t2.row(0 ) )
    self.assertEqual( ( 3, 4 ), t2.row(1 ) )
    
  def test___init__with_dimensions(self):
    t = table(10, 10)
    self.assertEqual( 10, t.width )
    self.assertEqual( 10, t.height )

  def test_get_empty(self):
    t = table(10, 10)
    self.assertEqual( None, t.get(0, 0) )

  def test_set_get(self):
    t = table(2, 2)
    t.set(0, 0, 1)
    t.set(0, 1, 2)
    t.set(1, 0, 3)
    t.set(1, 1, 4)
    self.assertEqual( 1, t.get(0, 0) )
    self.assertEqual( 2, t.get(0, 1) )
    self.assertEqual( 3, t.get(1, 0) )
    self.assertEqual( 4, t.get(1, 1) )

  def test_resize_shrink(self):
    t = table(3, 3)
    t.set(0, 0, 1)
    t.set(0, 1, 2)
    t.set(0, 2, 3)
    t.set(1, 0, 4)
    t.set(1, 1, 5)
    t.set(1, 2, 6)
    self.assertEqual( 3, t.width )
    self.assertEqual( 3, t.height )
    self.assertEqual( 1, t.get(0, 0) )
    self.assertEqual( 2, t.get(0, 1) )
    self.assertEqual( 3, t.get(0, 2) )
    self.assertEqual( 4, t.get(1, 0) )
    self.assertEqual( 5, t.get(1, 1) )
    self.assertEqual( 6, t.get(1, 2) )
    t.resize(2, 2)
    self.assertEqual( 2, t.width )
    self.assertEqual( 2, t.height )
    self.assertEqual( 1, t.get(0, 0) )
    self.assertEqual( 2, t.get(0, 1) )
    self.assertEqual( 4, t.get(1, 0) )
    self.assertEqual( 5, t.get(1, 1) )

  def test_resize_grow(self):
    t = table(3, 3)
    t.set(0, 0, 1)
    t.set(0, 1, 2)
    t.set(0, 2, 3)
    t.set(1, 0, 4)
    t.set(1, 1, 5)
    t.set(1, 2, 6)
    self.assertEqual( 3, t.width )
    self.assertEqual( 3, t.height )
    self.assertEqual( 1, t.get(0, 0) )
    self.assertEqual( 2, t.get(0, 1) )
    self.assertEqual( 3, t.get(0, 2) )
    self.assertEqual( 4, t.get(1, 0) )
    self.assertEqual( 5, t.get(1, 1) )
    self.assertEqual( 6, t.get(1, 2) )
    t.resize(4, 4)
    self.assertEqual( 1, t.get(0, 0) )
    self.assertEqual( 2, t.get(0, 1) )
    self.assertEqual( 3, t.get(0, 2) )
    self.assertEqual( None, t.get(0, 3) )
    self.assertEqual( 4, t.get(1, 0) )
    self.assertEqual( 5, t.get(1, 1) )
    self.assertEqual( 6, t.get(1, 2) )
    self.assertEqual( None, t.get(1, 3) )

  def test_set_data(self):
    t = table(3, 3)
    data = [
      ( 1, 2, 3 ),
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
    ]
    t.set_data(data)
    self.assertEqual( ( 1, 2, 3 ), t.row(0) )
    self.assertEqual( ( 4, 5, 6 ), t.row(1) )
    self.assertEqual( ( 7, 8, 9 ), t.row(2) )
    
  def test_row(self):
    t = table(3, 3, [
      ( 1, 2, 3 ),
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
    ])
    self.assertEqual( ( 1, 2, 3 ), t.row(0) )
    self.assertEqual( ( 4, 5, 6 ), t.row(1) )
    self.assertEqual( ( 7, 8, 9 ), t.row(2) )
    
  def test_col(self):
    t = table(3, 3, [
      ( 1, 2, 3 ),
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
    ])
    self.assertEqual( ( 1, 4, 7 ), t.column(0) )
    self.assertEqual( ( 2, 5, 8 ), t.column(1) )
    self.assertEqual( ( 3, 6, 9 ), t.column(2) )

  def test__eq__(self):
    t1 = table(data = [
      ( 1, 2, 3 ),
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
    ])
    t2 = table(data = [
      ( 1, 2, 3 ),
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
    ])
    t3 = table(data = [
      ( 99, 2, 3 ),
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
    ])
    self.assertTrue( t1 == t2 )
    self.assertFalse( t1 == t3 )
    
  def test_insert_column(self):
    t1 = table(data = [
      ( 1, 2, 3 ),
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
    ])
    t2 = table(data = [
      ( 1, 9, 2, 3 ),
      ( 4, 8, 5, 6 ),
      ( 7, 7, 8, 9 ),
    ])
    t1.insert_column(1, column = ( 9, 8, 7 ))
    self.assertEqual( t1, t2 )

  def test_insert_row(self):
    t1 = table(data = [
      ( 1, 2, 3 ),
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
    ], default_value = 0)
    t2 = table(data = [
      ( 1, 2, 3 ),
      ( 11, 12, 13 ),
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
    ])
    t1.insert_row(1, row = ( 11, 12, 13 ))
    self.assertEqual( t1, t2 )
    
  def test_append_rows(self):
    t1 = table(data = [
      ( 1, 2, 3 ),
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
    ])
    t2 = table(data = [
      ( 10, 11, 12 ),
      ( 13, 14, 15 ),
      ( 16, 17, 18 ),
    ])
    t1.append_rows(t2)
    t3 = table(data = [
      ( 1, 2, 3 ),
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
      ( 10, 11, 12 ),
      ( 13, 14, 15 ),
      ( 16, 17, 18 ),
    ])
    self.assertEqual( t3, t1 )
    
  def test_concatenate_vertical(self):
    t1 = table(data = [
      ( 1, 2, 3 ),
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
    ])
    t2 = table(data = [
      ( 10, 11, 12 ),
      ( 13, 14, 15 ),
      ( 16, 17, 18 ),
    ])
    t3 = table(data = [
      ( 99, 98, 97 ),
    ])
    t4 = table(data = [
      ( 1, 2, 3 ),
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
      ( 10, 11, 12 ),
      ( 13, 14, 15 ),
      ( 16, 17, 18 ),
      ( 99, 98, 97 ),
    ])
    self.assertEqual( t4, table.concatenate_vertical([ t1, t2, t3 ]) )

  def test_column_names(self):
    column_names = ( 'fruit', 'color', 'sweetness' )
    t = table(data = [
      ( 'cherry', 'red', 4 ),
      ( 'lemon', 'yellow', 2 ),
      ( 'orange', 'orange', 8 ),
      ( 'mango', 'orange', 10 ),
    ], column_names = column_names)
    self.assertEqual( 'cherry', t[0].fruit )
    self.assertEqual( 'lemon', t[1].fruit )
    self.assertEqual( 'orange', t[2].fruit )
    self.assertEqual( 'mango', t[3].fruit )
    self.assertEqual( 'red', t[0].color )
    self.assertEqual( 'yellow', t[1].color )
    self.assertEqual( 'orange', t[2].color )
    self.assertEqual( 'orange', t[3].color )
    self.assertEqual( 4, t[0].sweetness )
    self.assertEqual( 2, t[1].sweetness )
    self.assertEqual( 8, t[2].sweetness )
    self.assertEqual( 10, t[3].sweetness )

    with self.assertRaises(ValueError) as ex:
      t[0].nothere

if __name__ == '__main__':
  unit_test.main()
