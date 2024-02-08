#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.btl.btl_parser_node_creator import btl_parser_node_creator
from bes.btl.btl_lexer_token import btl_lexer_token
from bes.testing.unit_test import unit_test

class test_btl_parser_node_creator(unit_test):

  def xtest_create_root(self):
    nc = btl_parser_node_creator()
    self.assertEqual( False, nc.has_node('n_root') )
    nc.create_root()
    self.assertEqual( True, nc.has_node('n_root') )

  def test_create(self):
    nc = btl_parser_node_creator()
    nc.create_root()
    nc.create('n_kv')

    #name, value, position, type_hint')):
    btl_lexer_token('t_key', 'color')
    
    nc.create('n_key')
    nc.set_token('n_key', btl_lexer_token('t_key', 'color'))
    nc.add_child('n_kv', 'n_key')
    
    nc.create('n_value')
    nc.set_token('n_value', btl_lexer_token('t_value', 'red'))
    nc.add_child('n_kv', 'n_value')
    
    nc.add_child('n_root', 'n_kv')

    n = nc.get_root_node()
    self.assert_string_equal_fuzzy( '''
n_root;
  n_kv;
    n_key;t_key:color:1,1
    n_value;t_value:red:1,1
''', str(n) )
    
if __name__ == '__main__':
  unit_test.main()
