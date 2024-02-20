#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.btl.btl_parser_node import btl_parser_node
from bes.btl.btl_error import btl_error
from bes.testing.unit_test import unit_test

class test_btl_parser_node(unit_test):

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
    
if __name__ == '__main__':
  unit_test.main()
