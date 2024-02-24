#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.btl.btl_parser_node import btl_parser_node
from bes.btl.btl_parser_tester_mixin import btl_parser_tester_mixin
from bes.btl.btl_error import btl_error
from bes.testing.unit_test import unit_test

class test_btl_parser_node(btl_parser_tester_mixin, unit_test):

  def test_add_child(self):
    root = btl_parser_node('root')
    kiwi = btl_parser_node('kiwi')
    lemon = btl_parser_node('lemon')
    melon = btl_parser_node('melon')
    root.add_child(kiwi)
    root.add_child(lemon)
    root.add_child(melon)
    self.assert_python_code_text_equal( '''
root;
  kiwi;
  lemon;
  melon;
''', str(root) )

  def test_remove_child(self):
    root = btl_parser_node('root')
    kiwi = btl_parser_node('kiwi')
    lemon = btl_parser_node('lemon')
    melon = btl_parser_node('melon')
    root.add_child(kiwi)
    root.add_child(lemon)
    root.add_child(melon)
    root.remove_child(lemon)
    self.assert_python_code_text_equal( '''
root;
  kiwi;
  melon;
''', str(root) )

  def test_find_last_node(self):
    tree_text = '''
n_root;
  n_key_value;
    n_key;t_key:fruit:p=2,1:i=1
    n_value;t_value:apple:p=2,7:i=3
  n_key_value;
    n_key;t_key:color:p=3,1:i=5
    n_value;t_value:red:p=3,7:i=7
  n_key_value;
    n_key;t_key:fruit:p=5,1:i=10
    n_value;t_value:kiwi:p=5,7:i=12
  n_key_value;
    n_key;t_key:color:p=6,1:i=14
    n_value;t_value:green:p=6,7:i=16
'''
    root = self.parse_test_tree(tree_text)
    n = root.find_last_node()
    self.assertEqual( 'n_value;t_value:green:p=6,7:i=16', str(n) )
    
if __name__ == '__main__':
  unit_test.main()
