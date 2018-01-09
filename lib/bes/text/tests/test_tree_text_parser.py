#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.text import tree_text_parser as P
from bes.text.tree_text_parser import _text_stack
from bes.common import node
PI = _text_stack.path_item

class test_tree_text_parser(unittest.TestCase):

  @staticmethod
  def _data_func(data):
    return str(data) # data.line

  def test_simple1(self):
    self.maxDiff = None
    text = '''
fruits
  apple
  kiwi
'''
    expected = node(PI('root', 0))
    expected.ensure_path([ PI('fruits', 2), PI('apple', 3) ])
    expected.ensure_path([ PI('fruits', 2), PI('kiwi', 4) ])

    self.assertMultiLineEqual( expected.to_string(data_func = self._data_func), self._parse(text) )
    
  def test_simple2(self):
    self.maxDiff = None
    text = '''
fruits
  apple
  berries
    blueberries
    strawberries
  melons
    watermelon
cheeses
  parmessan
  asiago
'''
    expected = node(PI('root', 0))
    expected.ensure_path([ PI('fruits', 2), PI('apple', 3) ])
    expected.ensure_path([ PI('fruits', 2), PI('berries', 4), PI('blueberries', 5) ])
    expected.ensure_path([ PI('fruits', 2), PI('berries', 4), PI('strawberries', 6) ])
    expected.ensure_path([ PI('fruits', 2), PI('melons', 7), PI('watermelon', 8) ])
    expected.ensure_path([ PI('cheeses', 9), PI('parmessan', 10) ])
    expected.ensure_path([ PI('cheeses', 9), PI('asiago', 11) ])

    self.assertMultiLineEqual( expected.to_string(data_func = self._data_func), self._parse(text) )
    
  def test_inconsistent_indent(self):
    text = '''
fruits
    apple
    berries
      blueberries
      strawberries
    melons
      watermelon
cheeses
    parmessan
    asiago
'''
    expected = node(PI('root', 0))
    expected.ensure_path([ PI('fruits', 2), PI('apple', 3) ])
    expected.ensure_path([ PI('fruits', 2), PI('berries', 4), PI('blueberries', 5) ])
    expected.ensure_path([ PI('fruits', 2), PI('berries', 4), PI('strawberries', 6) ])
    expected.ensure_path([ PI('fruits', 2), PI('melons', 7), PI('watermelon', 8) ])
    expected.ensure_path([ PI('cheeses', 9), PI('parmessan', 10) ])
    expected.ensure_path([ PI('cheeses', 9), PI('asiago', 11) ])
    
    self.assertMultiLineEqual( str(expected), self._parse(text) )
    
  def test_indent_tabs(self):
    text = '''
fruits
\t\tapple
\t\tberries
\t\t\tblueberries
\t\t\tstrawberries
\t\tmelons
\t\t\twatermelon
cheeses
\t\tparmessan
\t\tasiago
'''
    expected = node(PI('root', 0))
    expected.ensure_path([ PI('fruits', 2), PI('apple', 3) ])
    expected.ensure_path([ PI('fruits', 2), PI('berries', 4), PI('blueberries', 5) ])
    expected.ensure_path([ PI('fruits', 2), PI('berries', 4), PI('strawberries', 6) ])
    expected.ensure_path([ PI('fruits', 2), PI('melons', 7), PI('watermelon', 8) ])
    expected.ensure_path([ PI('cheeses', 9), PI('parmessan', 10) ])
    expected.ensure_path([ PI('cheeses', 9), PI('asiago', 11) ])
    
    self.assertMultiLineEqual( str(expected), self._parse(text) )
    
  def test_indent_mixed_tabs_spaces(self):
    text = '''
fruits
  apple
  berries
  \tblueberries
  \tstrawberries
  melons
  \twatermelon
cheeses
  parmessan
  asiago
'''
    expected = node(PI('root', 0))
    expected.ensure_path([ PI('fruits', 2), PI('apple', 3) ])
    expected.ensure_path([ PI('fruits', 2), PI('berries', 4), PI('blueberries', 5) ])
    expected.ensure_path([ PI('fruits', 2), PI('berries', 4), PI('strawberries', 6) ])
    expected.ensure_path([ PI('fruits', 2), PI('melons', 7), PI('watermelon', 8) ])
    expected.ensure_path([ PI('cheeses', 9), PI('parmessan', 10) ])
    expected.ensure_path([ PI('cheeses', 9), PI('asiago', 11) ])
    
    self.assertMultiLineEqual( str(expected), self._parse(text) )

  def test_strip_comments(self):
    self.maxDiff = None
    text = '''
# comment
fruits # comment
  # comment
  apple
  # comment
  kiwi
# comment
'''
    expected = node(PI('root', 0))
    expected.ensure_path([ PI('fruits', 3), PI('apple', 5) ])
    expected.ensure_path([ PI('fruits', 3), PI('kiwi', 7) ])

    self.assertMultiLineEqual( expected.to_string(data_func = self._data_func), self._parse(text, strip_comments = True) )

  def test_node_text_recursive_one_node(self):
    text = '''
fruits
'''
    self.assertEqual( 'root fruits', P.node_text_recursive(P.parse(text)) )

  def test_node_text_recursive_two_nodes(self):
    text = '''
fruits
  apple
  berries
    blueberries
      strawberries
'''
    self.assertEqual( 'root fruits apple berries blueberries strawberries', P.node_text_recursive(P.parse(text)) )


  @classmethod
  def _parse(clazz, text, strip_comments = False):
    return P.parse(text, strip_comments = strip_comments).to_string(data_func = clazz._data_func)
    
if __name__ == "__main__":
  unittest.main()
