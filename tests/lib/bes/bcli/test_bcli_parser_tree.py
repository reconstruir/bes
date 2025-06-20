#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.testing.unit_test import unit_test

from bes.bcli.bcli_parser_tree import bcli_parser_tree

class test_bcli_parser_tree(unit_test):

  def test_foo(self):
    t = bcli_parser_tree()
    t.set([ 'kitchen', 'cook' ], 'value1')
    n = t.get([ 'kitchen', 'cook' ])
    print(f'n={n}')

  def test_get_safe_existing_path(self):
    tree = bcli_parser_tree()
    tree.set(['kitchen', 'cook'], 'value1')

    actual_path, node = tree.get_safe(['kitchen', 'cook'])
    self.assertEqual(actual_path, ['kitchen', 'cook'])
    self.assertIsNotNone(node)
    self.assertEqual(node.value, 'value1')

  def test_get_safe_existing_path_poto(self):
    tree = bcli_parser_tree()
    tree.set(['kitchen', 'cook'], 'value1')

    actual_path, node = tree.get_existing_prefix(['kitchen', 'cook', 'fuck'])
    print(f'actual_path={actual_path}')
    print(f'node={node}')
#    self.assertEqual(actual_path, ['kitchen', 'cook'])
#    self.assertIsNotNone(node)
#    self.assertEqual(node.value, 'value1')
    
  def test_get_safe_missing_path(self):
    tree = bcli_parser_tree()
    tree.set(['kitchen', 'cook'], 'value1')

    with self.assertRaises(KeyError) as context:
      tree.get_safe(['kitchen', 'prepare'])
    self.assertIn('kitchen/prepare', str(context.exception))

  def test_get_safe_partial_missing_path(self):
    tree = bcli_parser_tree()
    tree.set(['kitchen', 'cook'], 'value1')

    with self.assertRaises(KeyError) as context:
      tree.get_safe(['garage', 'open'])
    self.assertIn('garage', str(context.exception))
    
if __name__ == '__main__':
  unit_test.main()
