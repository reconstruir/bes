#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.btl.btl_lexer_desc_header import btl_lexer_desc_header
from bes.btl.btl_error import btl_error
from bes.testing.unit_test import unit_test
from bes.text.tree_text_parser import _text_node_data

from _test_simple_lexer_mixin import _test_simple_lexer_mixin

class test_btl_lexer_desc_header(_test_simple_lexer_mixin, unit_test):

  def test_parse_node(self):
    lexer_node = self._simple_lexer_desc_tree_section('lexer')
    self.assertEqual( (
      'l_simple',
      'A simple key value pair lexer',
      '1.0',
      's_start',
      's_done',
    ), btl_lexer_desc_header.parse_node(lexer_node) )

  def test_parse_node_invalid_key(self):
    lexer_node = self._simple_lexer_desc_tree_section('lexer')
    assert lexer_node.children[0].data.text == 'name: l_simple'
    lexer_node.children[0].data = _text_node_data('kiwi: green', lexer_node.children[0].data.line_number)
    with self.assertRaises(btl_error) as ctx:
      btl_lexer_desc_header.parse_node(lexer_node)
    self.assertEqual( True, 'Invalid header key "kiwi" at <unknown>' in ctx.exception.message )

  def test_parse_node_missing_key(self):
    lexer_node = self._simple_lexer_desc_tree_section('lexer')
    lexer_node.children = lexer_node.children[0:-2]
    with self.assertRaises(btl_error) as ctx:
      btl_lexer_desc_header.parse_node(lexer_node)
    self.assertEqual( True, 'Missing key "start_state" at <unknown>' in ctx.exception.message )
    
if __name__ == '__main__':
  unit_test.main()
