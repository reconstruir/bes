#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.common.table import table

class test_table(unit_test):

  def test___init__empty(self):
    t = table()
    self.assertEqual( 0, t.width )
    self.assertEqual( 0, t.height )

  def test_empty(self):
    t1 = table()
    self.assertTrue( t1.empty )
    t2 =  table(data = [
      ( 1, 2 ),
      ( 3, 4 ),
    ])
    self.assertFalse( t2.empty )

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

  def test___init__with_one_row(self):
    t =  table(data = [
      ( 1, 2, 3 ),
    ])
    self.assertEqual( 3, t.width )
    self.assertEqual( 1, t.height )
    
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

  def test_col_with_name(self):
    column_names = ( 'fruit', 'color', 'sweetness' )
    t = table(data = [
      ( 'cherry', 'red', 4 ),
      ( 'lemon', 'yellow', 2 ),
      ( 'orange', 'orange', 8 ),
      ( 'mango', 'orange', 10 ),
    ], column_names = column_names)
    self.assertEqual( ( 'cherry', 'lemon', 'orange', 'mango' ), t.column('fruit') )
    self.assertEqual( ( 'red', 'yellow', 'orange', 'orange' ), t.column('color') )
    self.assertEqual( ( 4, 2, 8, 10 ), t.column('sweetness') )
    
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

  def test__eq__seq(self):
    t1 = table(data = [
      ( 1, 2, 3 ),
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
    ])
    t2 = [
      ( 1, 2, 3 ),
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
    ]
    t3 = [
      [ 1, 2, 3 ],
      [ 4, 5, 6 ],
      [ 7, 8, 9 ],
    ]
    t4 = (
      [ 1, 2, 3 ],
      [ 4, 5, 6 ],
      [ 7, 8, 9 ],
    )
    t5 = [
      ( 99, 2, 3 ),
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
    ]
    self.assertTrue( t1 == t2 )
    self.assertTrue( t1 == t3 )
    self.assertTrue( t1 == t4 )
    self.assertFalse( t1 == t5 )
    
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

  def test_insert_column_empty_table(self):
    t1 = table()
    t2 = table(data = [
      ( 1, ),
      ( 2, ),
      ( 3, ),
    ])
    t1.insert_column(0, column = ( 1, 2, 3 ))
    self.assertEqual( t1, t2 )
    
  def test_insert_row_empty_table(self):
    t1 = table()
    t2 = table(data = [
      ( 1, 2, 3 ),
    ])
    t1.insert_row(0, row = ( 1, 2, 3 ))
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

  def test_column_names_setter(self):
    column_names = ( 'fruit', 'color', 'sweetness' )
    t = table(data = [
      ( 'cherry', 'red', 4 ),
      ( 'lemon', 'yellow', 2 ),
      ( 'orange', 'orange', 8 ),
      ( 'mango', 'orange', 10 ),
    ], column_names = column_names)
    self.assertEqual( 'red', t[0].color )
    t[0].color = 'purple'
    self.assertEqual( 'purple', t[0].color )

    with self.assertRaises(ValueError) as ex:
      t[0].nothere = 666
    
  def test_concatenate_vertical_with_column_names(self):
    column_names = ( 'one', 'two', 'three' )
    t1 = table(data = [
      ( 1, 2, 3 ),
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
    ], column_names = column_names)
    t2 = table(data = [
      ( 10, 11, 12 ),
      ( 13, 14, 15 ),
      ( 16, 17, 18 ),
    ])
    t3 = table(data = [
      ( 99, 98, 97 ),
    ], column_names = column_names)
    actual = table.concatenate_vertical([ t1, t2, t3 ])
    expected = table(data = [
      ( 1, 2, 3 ),
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
      ( 10, 11, 12 ),
      ( 13, 14, 15 ),
      ( 16, 17, 18 ),
      ( 99, 98, 97 ),
    ])
    self.assertEqual( 1, t1[0].one )
    self.assertEqual( 2, t1[0].two )
    self.assertEqual( 3, t1[0].three )
    self.assertEqual( 1, actual[0].one )
    self.assertEqual( 2, actual[0].two )
    self.assertEqual( 3, actual[0].three )
    self.assertEqual( expected, actual )

  def test_concatenate_vertical_one_table_with_column_names(self):
    column_names = ( 'one', 'two', 'three' )
    t1 = table(data = [
      ( 1, 2, 3 ),
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
    ], column_names = column_names)
    actual = table.concatenate_vertical([ t1 ])
    expected = table(data = [
      ( 1, 2, 3 ),
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
    ])
    self.assertEqual( 1, t1[0].one )
    self.assertEqual( 2, t1[0].two )
    self.assertEqual( 3, t1[0].three )
    self.assertEqual( 1, actual[0].one )
    self.assertEqual( 2, actual[0].two )
    self.assertEqual( 3, actual[0].three )
    self.assertEqual( expected, actual )

  def test_sort_by_column(self):
    column_names = ( 'fruit', 'color', 'sweetness' )
    t = table(data = [
      ( 'cherry', 'red', 4 ),
      ( 'lemon', 'yellow', 2 ),
      ( 'orange', 'orange', 8 ),
      ( 'mango', 'orange', 10 ),
    ], column_names = column_names)
    t.sort_by_column(0)
    self.assertEqual( table(data = [
      ( 'cherry', 'red', 4 ),
      ( 'lemon', 'yellow', 2 ),
      ( 'mango', 'orange', 10 ),
      ( 'orange', 'orange', 8 ),
    ]), t )
    t.sort_by_column(1)
    self.assertEqual( table(data = [
      ( 'mango', 'orange', 10 ),
      ( 'orange', 'orange', 8 ),
      ( 'cherry', 'red', 4 ),
      ( 'lemon', 'yellow', 2 ),
    ]), t )
    t.sort_by_column(2)
    self.assertEqual( table(data = [
      ( 'lemon', 'yellow', 2 ),
      ( 'cherry', 'red', 4 ),
      ( 'orange', 'orange', 8 ),
      ( 'mango', 'orange', 10 ),
    ]), t )
      
  def test_sort_by_key(self):
    column_names = ( 'fruit', 'color', 'sweetness' )
    t = table(data = [
      ( 'cherry', 'red', 4 ),
      ( 'lemon', 'yellow', 2 ),
      ( 'orange', 'orange', 8 ),
      ( 'mango', 'orange', 10 ),
    ], column_names = column_names)
    t.sort_by_key((lambda row: row.fruit))
    self.assertEqual( table(data = [
      ( 'cherry', 'red', 4 ),
      ( 'lemon', 'yellow', 2 ),
      ( 'mango', 'orange', 10 ),
      ( 'orange', 'orange', 8 ),
    ]), t )
    t.sort_by_key((lambda row: row.color))
    self.assertEqual( table(data = [
      ( 'mango', 'orange', 10 ),
      ( 'orange', 'orange', 8 ),
      ( 'cherry', 'red', 4 ),
      ( 'lemon', 'yellow', 2 ),
    ]), t )
    t.sort_by_key((lambda row: row.sweetness))
    self.assertEqual( table(data = [
      ( 'lemon', 'yellow', 2 ),
      ( 'cherry', 'red', 4 ),
      ( 'orange', 'orange', 8 ),
      ( 'mango', 'orange', 10 ),
    ]), t )

  def test_concatenate_vertical_with_empty_table(self):
    t1 = table(data = [
      ( 1, 2, 3 ),
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
    ])
    t2 = table()
    t3 = table(data = [
      ( 99, 98, 97 ),
    ])
    t4 = table(data = [
      ( 1, 2, 3 ),
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
      ( 99, 98, 97 ),
    ])
    self.assertEqual( t4, table.concatenate_vertical([ t1, t2, t3 ]) )
    
  def test_concatenate_vertical_all_empty(self):
    t1 = table()
    t2 = table()
    t3 = table()
    t4 = table()
    self.assertEqual( t4, table.concatenate_vertical([ t1, t2, t3 ]) )

  def test_remove_column(self):
    t1 = table(data = [
      ( 1, 2, 3 ),
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
    ])
    t2 = table(data = [
      ( 1, 3 ),
      ( 4, 6 ),
      ( 7, 9 ),
    ])
    t1.remove_column(1)
    self.assertEqual( t1, t2 )
    t3 = table(data = [
      ( 3, ),
      ( 6, ),
      ( 9, ),
    ])
    t1.remove_column(0)
    self.assertEqual( t1, t3 )

  def test_insert_column_with_names(self):
    column_names = ( 'fruit', 'sweetness' )
    t1 = table(data = [
      ( 'cherry', 4),
      ( 'lemon', 2 ),
      ( 'orange', 8 ),
      ( 'mango', 10 ),
    ], column_names = column_names)
    t1.insert_column(1, column = ( 'red', 'yellow', 'orange', 'orange' ), name = 'color')
    t2 = table(data = [
      ( 'cherry', 'red', 4 ),
      ( 'lemon', 'yellow', 2 ),
      ( 'orange', 'orange', 8 ),
      ( 'mango', 'orange', 10 ),
    ], column_names = column_names)
    self.assertEqual( t1, t2 )

  def test_append_column_with_names(self):
    t = table(data = [
      ( 'cherry', 4),
      ( 'lemon', 2 ),
      ( 'orange', 8 ),
      ( 'mango', 10 ),
    ], column_names = ( 'fruit', 'sweetness' ))
    t.insert_column(2, name = 'color')
#    t2 = table(data = [
#      ( 'cherry', 'red', 4 ),
#      ( 'lemon', 'yellow', 2 ),
#      ( 'orange', 'orange', 8 ),
#      ( 'mango', 'orange', 10 ),
#    ], column_names = column_names)
    self.assertEqual( [
      ( 'cherry', 4, None ),
      ( 'lemon', 2, None ),
      ( 'orange', 8, None ),
      ( 'mango', 10, None ),
    ], t )
    t[0].color = 'red'
    t[1].color = 'yellow'
    t[2].color = 'orange'
    t[3].color = 'orange'
    self.assertEqual( [
      ( 'cherry', 4, 'red' ),
      ( 'lemon', 2, 'yellow' ),
      ( 'orange', 8, 'orange' ),
      ( 'mango', 10, 'orange' ),
    ], t )
    
  def test_resolve_x(self):
    column_names = ( 'fruit', 'color', 'sweetness' )
    t = table(data = [
      ( 'cherry', 'red', 4 ),
      ( 'lemon', 'yellow', 2 ),
      ( 'orange', 'orange', 8 ),
      ( 'mango', 'orange', 10 ),
    ], column_names = column_names)
    
    self.assertEqual( 0, t.resolve_x(0) )
    self.assertEqual( 1, t.resolve_x(1) )
    self.assertEqual( 2, t.resolve_x(2) )
    with self.assertRaises(ValueError) as ex:
      t.resolve_x(3)
    
    self.assertEqual( 0, t.resolve_x('fruit') )
    self.assertEqual( 1, t.resolve_x('color') )
    self.assertEqual( 2, t.resolve_x('sweetness') )
    with self.assertRaises(ValueError) as ex:
      t.resolve_x('notthere')
    
  def test_remove_column_with_name(self):
    column_names = ( 'fruit', 'color', 'sweetness' )
    t1 = table(data = [
      ( 'cherry', 'red', 4 ),
      ( 'lemon', 'yellow', 2 ),
      ( 'orange', 'orange', 8 ),
      ( 'mango', 'orange', 10 ),
    ], column_names = column_names)
    t1.remove_column('color')
    t2 = table(data = [
      ( 'cherry', 4),
      ( 'lemon', 2 ),
      ( 'orange', 8 ),
      ( 'mango', 10 ),
    ], column_names = column_names)
    self.assertEqual( t1, t2 )

    with self.assertRaises(ValueError) as ex:
      t1.remove_column('notthere')

  def test_to_csv(self):
    column_names = ( 'fruit', 'color', 'sweetness' )
    t1 = table(data = [
      ( 'cherry', 'red', 4 ),
      ( 'lemon', 'yellow', 2 ),
      ( 'orange', 'orange', 8 ),
      ( 'mango', 'orange', 10 ),
    ], column_names = column_names)
    self.assertEqual( 'cherry,red,4\r\nlemon,yellow,2\r\norange,orange,8\r\nmango,orange,10\r\n', t1.to_csv() )
      
  def test_from_csv(self):
    text = '''
cherry,red,4
lemon,yellow,2
orange,orange,8
mango,orange,10
'''      

    t1 = table.from_csv(text)
    column_names = ( 'fruit', 'color', 'sweetness' )
    t2 = table(data = [
      ( 'cherry', 'red', '4' ),
      ( 'lemon', 'yellow', '2' ),
      ( 'orange', 'orange', '8' ),
      ( 'mango', 'orange', '10' ),
    ], column_names = column_names)
    self.assertEqual( t1, t2 )

  def test_get_column_names(self):
    column_names = ( 'fruit', 'color', 'sweetness' )
    t = table(data = [
      ( 'cherry', 'red', 4 ),
      ( 'lemon', 'yellow', 2 ),
    ], column_names = column_names)
    self.assertEqual( column_names, t.column_names )
    
  def test_set_column_names(self):
    t = table(data = [
      ( 'cherry', 'red', 4 ),
      ( 'lemon', 'yellow', 2 ),
      ( 'orange', 'orange', 8 ),
      ( 'mango', 'orange', 10 ),
    ], column_names = ( 'fruit', 'color', 'sweetness' ))
    self.assertEqual( 'cherry', t[0].fruit )
    self.assertEqual( 'red', t[0].color )
    self.assertEqual( 4, t[0].sweetness )
    t.column_names = ( 'fruit2', 'color2', 'sweetness2' )

    with self.assertRaises(ValueError) as ex:
      t[0].fruit
    with self.assertRaises(ValueError) as ex:
      t[0].color
    with self.assertRaises(ValueError) as ex:
      t[0].sweetness

    self.assertEqual( 'cherry', t[0].fruit2 )
    self.assertEqual( 'red', t[0].color2 )
    self.assertEqual( 4, t[0].sweetness2 )

  def test_to_json(self):
    t = table(data = [
      ( 'cherry', 'red', 4 ),
      ( 'lemon', 'yellow', 2 ),
      ( 'orange', 'orange', 8 ),
      ( 'mango', 'orange', 10 ),
    ])
    expected = '''
[
  [
    "cherry",
    "red",
    4
  ],
  [
    "lemon",
    "yellow",
    2
  ],
  [
    "orange",
    "orange",
    8
  ],
  [
    "mango",
    "orange",
    10
  ]
]
'''
    self.assertEqualIgnoreWhiteSpace( expected, t.to_json() )

  def test_from_json(self):
    text = '''
[
  [
    "cherry",
    "red",
    4
  ],
  [
    "lemon",
    "yellow",
    2
  ],
  [
    "orange",
    "orange",
    8
  ],
  [
    "mango",
    "orange",
    10
  ]
]
'''

    t = table.from_json(text)
    
    expected = table(data = [
      ( 'cherry', 'red', 4 ),
      ( 'lemon', 'yellow', 2 ),
      ( 'orange', 'orange', 8 ),
      ( 'mango', 'orange', 10 ),
    ])
    self.assertEqual( expected, t )

  def test_remove_row(self):
    t1 = table(data = [
      ( 1, 2, 3 ),
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
    ])
    t2 = table(data = [
      ( 4, 5, 6 ),
      ( 7, 8, 9 ),
    ])
    t3 = table(data = [
      ( 4, 5, 6 ),
    ])
    t4 = table(data = [])

    t1.remove_row(0)
    self.assertEqual( t1, t2 )

    t1.remove_row(1)
    self.assertEqual( t1, t3 )

    t1.remove_row(0)
    self.assertEqual( t1, t4 )

  def test_remove_row_with_key(self):
    self.maxDiff = None
    t = table(data = [
      ( 'cherry', 'red', 4 ),
      ( 'lemon', 'yellow', 2 ),
      ( 'orange', 'orange', 8 ),
      ( 'mango', 'orange', 10 ),
    ], column_names = ( 'fruit', 'color', 'sweetness' ))
    t.remove_row_with_key(lambda row: row.color == 'orange')
    self.assertEqual( [
      ( 'cherry', 'red', 4 ),
      ( 'lemon', 'yellow', 2 ),
    ], t )
    
if __name__ == '__main__':
  unit_test.main()
