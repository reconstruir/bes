#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.testing.unit_test import unit_test

from bes.bcli.bcli_parser_tree import bcli_parser_tree

class DummyHandler:
  def __init__(self, name):
    self._name = name
  def description(self):
    return f"Handler {self._name}"
  def __repr__(self):
    return f"<DummyHandler {self._name}>"
  
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

    actual_path, node, rest = tree.get_existing_prefix(['kitchen', 'cook', 'fuck', 'fpp'])
    print(f'actual_path={actual_path}')
    print(f'node={node}')
    print(f'rest={rest}')
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

  def test_get_safe_partial_missing_path(self):
    tree = bcli_parser_tree()
    tree.set(['kitchen', 'cook'], 'value1')

    with self.assertRaises(KeyError) as context:
      tree.get_safe(['garage', 'open'])
    self.assertIn('garage', str(context.exception))

  def test_exact_match(self):
    tree = bcli_parser_tree()
    tree.set(['vmware', 'vm', 'start'], DummyHandler('start'))
    actual_path, node = tree.get_safe_with_shortcuts(['vmware', 'vm', 'start'])
    self.assertEqual(actual_path, ['vmware', 'vm', 'start'])
    self.assertIsNotNone(node.value)
    self.assertEqual(node.value._name, 'start')

  def test_unique_prefix(self):
    tree = bcli_parser_tree()
    tree.set(['vmware', 'vm', 'start'], DummyHandler('start'))
    actual_path, node = tree.get_safe_with_shortcuts(['vmw', 'vm', 'st'])
    self.assertEqual(actual_path, ['vmware', 'vm', 'start'])
    self.assertEqual(node.value._name, 'start')

  def test_first_last_letters(self):
    tree = bcli_parser_tree()
    tree.set(['opnsense', 'dhcp', 'leases', 'show'], DummyHandler('show'))
    actual_path, node = tree.get_safe_with_shortcuts(['oe', 'dhcp', 'leases', 'show'])
    self.assertEqual(actual_path, ['opnsense', 'dhcp', 'leases', 'show'])
    self.assertEqual(node.value._name, 'show')

  def test_dash_initials(self):
    tree = bcli_parser_tree()
    tree.set(['something-foo', 'fruit', 'kiwi'], DummyHandler('kiwi'))
    actual_path, node = tree.get_safe_with_shortcuts(['sf', 'fruit', 'kiwi'])
    self.assertEqual(actual_path, ['something-foo', 'fruit', 'kiwi'])
    self.assertEqual(node.value._name, 'kiwi')

  def test_ambiguous_prefix(self):
    tree = bcli_parser_tree()
    tree.set(['vmware', 'vm', 'start'], DummyHandler('start'))
    tree.set(['vmware', 'vm', 'status'], DummyHandler('status'))
    with self.assertRaises(ValueError) as ctx:
      tree.get_safe_with_shortcuts(['vmware', 'vm', 'st'])
    self.assertIn("Ambiguous token 'st'", str(ctx.exception))

  def test_unrecognized_token(self):
    tree = bcli_parser_tree()
    with self.assertRaises(KeyError) as ctx:
      tree.get_safe_with_shortcuts(['doesnotexist'])
    self.assertIn("No subcommands under", str(ctx.exception))

  def test_partial_path(self):
    tree = bcli_parser_tree()
    tree.set(['vmware', 'vm', 'start'], DummyHandler('start'))
    with self.assertRaises(KeyError) as ctx:
      tree.get_safe_with_shortcuts(['vmware', 'bad'])
    self.assertIn("Unrecognized token 'bad'", str(ctx.exception))
    
if __name__ == '__main__':
  unit_test.main()
