#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
import unittest
from bes.text import tree_text_parser as P
from bes.text.tree_text_parser import _text_node_data as TDATA
from bes.common import node

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
    expected = node(TDATA('root', 0))
    expected.ensure_path([ TDATA('fruits', 2), TDATA('apple', 3) ])
    expected.ensure_path([ TDATA('fruits', 2), TDATA('kiwi', 4) ])

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
    expected = node(TDATA('root', 0))
    expected.ensure_path([ TDATA('fruits', 2), TDATA('apple', 3) ])
    expected.ensure_path([ TDATA('fruits', 2), TDATA('berries', 4), TDATA('blueberries', 5) ])
    expected.ensure_path([ TDATA('fruits', 2), TDATA('berries', 4), TDATA('strawberries', 6) ])
    expected.ensure_path([ TDATA('fruits', 2), TDATA('melons', 7), TDATA('watermelon', 8) ])
    expected.ensure_path([ TDATA('cheeses', 9), TDATA('parmessan', 10) ])
    expected.ensure_path([ TDATA('cheeses', 9), TDATA('asiago', 11) ])

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
    expected = node(TDATA('root', 0))
    expected.ensure_path([ TDATA('fruits', 2), TDATA('apple', 3) ])
    expected.ensure_path([ TDATA('fruits', 2), TDATA('berries', 4), TDATA('blueberries', 5) ])
    expected.ensure_path([ TDATA('fruits', 2), TDATA('berries', 4), TDATA('strawberries', 6) ])
    expected.ensure_path([ TDATA('fruits', 2), TDATA('melons', 7), TDATA('watermelon', 8) ])
    expected.ensure_path([ TDATA('cheeses', 9), TDATA('parmessan', 10) ])
    expected.ensure_path([ TDATA('cheeses', 9), TDATA('asiago', 11) ])
    
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
    expected = node(TDATA('root', 0))
    expected.ensure_path([ TDATA('fruits', 2), TDATA('apple', 3) ])
    expected.ensure_path([ TDATA('fruits', 2), TDATA('berries', 4), TDATA('blueberries', 5) ])
    expected.ensure_path([ TDATA('fruits', 2), TDATA('berries', 4), TDATA('strawberries', 6) ])
    expected.ensure_path([ TDATA('fruits', 2), TDATA('melons', 7), TDATA('watermelon', 8) ])
    expected.ensure_path([ TDATA('cheeses', 9), TDATA('parmessan', 10) ])
    expected.ensure_path([ TDATA('cheeses', 9), TDATA('asiago', 11) ])
    
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
    expected = node(TDATA('root', 0))
    expected.ensure_path([ TDATA('fruits', 2), TDATA('apple', 3) ])
    expected.ensure_path([ TDATA('fruits', 2), TDATA('berries', 4), TDATA('blueberries', 5) ])
    expected.ensure_path([ TDATA('fruits', 2), TDATA('berries', 4), TDATA('strawberries', 6) ])
    expected.ensure_path([ TDATA('fruits', 2), TDATA('melons', 7), TDATA('watermelon', 8) ])
    expected.ensure_path([ TDATA('cheeses', 9), TDATA('parmessan', 10) ])
    expected.ensure_path([ TDATA('cheeses', 9), TDATA('asiago', 11) ])
    
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
    expected = node(TDATA('root', 0))
    expected.ensure_path([ TDATA('fruits', 3), TDATA('apple', 5) ])
    expected.ensure_path([ TDATA('fruits', 3), TDATA('kiwi', 7) ])

    self.assertMultiLineEqual( expected.to_string(data_func = self._data_func), self._parse(text, strip_comments = True) )

  def test_strip_quote_in_comments(self):
    self.maxDiff = None
    text = '''
fruits
  apple
  kiwi
###              fprintf(stderr, "Usage: cut.exe args\\n");
'''
    expected = node(TDATA('root', 0))
    expected.ensure_path([ TDATA('fruits', 2), TDATA('apple', 3) ])
    expected.ensure_path([ TDATA('fruits', 2), TDATA('kiwi', 4) ])

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

  def test__fold_literals(self):
    text = '''\
child1

child2
  sub2a
    sub2a1
  sub2b
    > this is a multi
      line literal
      that includes \'\'\'whatever\'\'\'

  sub2c
    foo
  sub2d
    >this is a another multi
     #
     line literal


  sub2e
    >    this is yet another multi

         #
         line literal
         foo
  sub3d'''
    from bes.text import text_line_parser
    parser = text_line_parser(text)
    literals = P._fold_literals(parser)
    expected = '''\
child1

child2
  sub2a
    sub2a1
  sub2b
    @@tree_text_literal:0@@
  sub2c
    foo
  sub2d
    @@tree_text_literal:1@@
  sub2e
    @@tree_text_literal:2@@
  sub3d'''
    self.assertMultiLineEqual( expected, str(parser) )

    self.assertEqual( [ '@@tree_text_literal:0@@', '@@tree_text_literal:1@@', '@@tree_text_literal:2@@' ],
                      sorted(literals.keys()) )
    self.assertEqual( "this is a multi\nline literal\nthat includes '''whatever'''",
                      literals['@@tree_text_literal:0@@'].text )
    self.assertEqual( "this is a another multi\n#\nline literal\n",
                      literals['@@tree_text_literal:1@@'].text )
    self.assertEqual( "this is yet another multi\n\n#\nline literal",
                      literals['@@tree_text_literal:2@@'].text )

  def xtest_literals(self):
    tree_text = '''\
child1

child2
  sub2a
    sub2a1
  sub2b
    > this is a multi
      line literal
      that includes \'\'\'whatever\'\'\'

  sub2c
    foo
  sub2d
    >this is a another multi
     #
     line literal


  sub2e
    >    this is yet another multi

         #
         line literal
         foo
  sub3d'''
    root = P.parse(tree_text)
    expected = '''\
child1

child2
  sub2a
    sub2a1
  sub2b
    > this is a multi
      line literal
      that includes \'\'\'whatever\'\'\'

  sub2c
    foo
  sub2d
    >this is a another multi
     #
     line literal


  sub2e
    >    this is yet another multi

         #
         line literal
         foo
  sub3d'''

    child = root.find_child_by_text('blueberries')
    self.assertEqual( 'strawberries organic conventional', child.get_text(root.CHILDREN_FLAT) )
    
if __name__ == "__main__":
  unittest.main()
