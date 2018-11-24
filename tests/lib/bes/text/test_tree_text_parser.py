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

  def test_strip_quote_in_comments(self):
    self.maxDiff = None
    text = '''
fruits
  apple
  kiwi
###              fprintf(stderr, "Usage: cut.exe args\\n");
'''
    expected = node(PI('root', 0))
    expected.ensure_path([ PI('fruits', 2), PI('apple', 3) ])
    expected.ensure_path([ PI('fruits', 2), PI('kiwi', 4) ])

    self.assertMultiLineEqual( expected.to_string(data_func = self._data_func), self._parse(text, strip_comments = True) )

  def test_get_text_node(self):
    tree_text = '''
fruits
'''
    root = P.parse(tree_text)
    self.assertEqual( 'root', root.get_text(root.NODE) )
    
  def test_get_text_node_flat(self):
    tree_text = '''
fruits
'''
    root = P.parse(tree_text)
    self.assertEqual( 'root fruits', root.get_text(root.NODE_FLAT) )
    
  def test_get_text_node_flat_three_nodes(self):
    tree_text = '''
fruits
  apple
  berries
    blueberries
      strawberries
'''
    root = P.parse(tree_text)
    self.assertEqual( 'root fruits apple berries blueberries strawberries', root.get_text(root.NODE_FLAT) )
    
  def test_get_text_children_inline(self):
    tree_text = '''
c_program
  bin/cut.exe
    sources
      main.c
        int main(int argc, char* argv[]) {
        char* arg;
        if (argc < 2) {
          fprintf(stderr, "Usage: cut.exe args\\n");
          return 1;
        }
        return 0;
'''
    expected = '''int main(int argc, char* argv[]) {
char* arg;
if (argc < 2) {
  fprintf(stderr, "Usage: cut.exe args\\n");
  return 1;
}
return 0;
'''
    root = P.parse(tree_text)
    child = root.find_child_by_text('main.c')
    self.assertMultiLineEqual( expected, child.get_text(child.CHILDREN_INLINE) )

  def test_get_text_children_flat_three_nodes(self):
    tree_text = '''
fruits
  apple
  berries
    blueberries
      strawberries
        organic
        conventional
'''
    root = P.parse(tree_text)
    child = root.find_child_by_text('blueberries')
    self.assertEqual( 'strawberries organic conventional', child.get_text(root.CHILDREN_FLAT) )
    
  @classmethod
  def _parse(clazz, text, strip_comments = False, root_name = 'root'):
    root = P.parse(text, strip_comments = strip_comments, root_name = root_name)
    return root.to_string(data_func = clazz._data_func)
    
if __name__ == "__main__":
  unittest.main()
