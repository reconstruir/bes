#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import typing
from datetime import datetime
#from datetime import timedelta

from bes.testing.unit_test import unit_test

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc
from bes.bcli.bcli_simple_type_item_list import bcli_simple_type_item_list

class test_bcli_options(unit_test):

  def test_has_options(self):
    options = self._make_test_options()
    self.assertEqual( True, options.has_option('kiwi') )
    self.assertEqual( True, options.has_option('pear') )
    self.assertEqual( False, options.has_option('lemon') )

  def test___getattr__defaults(self):
    options = self._make_test_options()
    self.assertEqual( 42, options.kiwi )
    self.assertEqual( 666, options.pear )

  def test___getattr____setattr__(self):
    options = self._make_test_options()
    self.assertEqual( 42, options.kiwi )
    options.kiwi = 13
    self.assertEqual( 13, options.kiwi )

  def test___init__with_kwargs(self):
    options = self._make_test_options(kiwi = 100, pear = 101)
    self.assertEqual( 100, options.kiwi )
    self.assertEqual( 101, options.pear )

  def test___init__with_invalid_kwargs(self):
    with self.assertRaises(KeyError) as ctx:
      options = self._make_test_options(notthere = 1)

  def test_subclass(self):
    class _test_kiwi_options_shape(bcli_options_desc):
      def __init__(self):
        types = bcli_simple_type_item_list([
        ])
        items_desc = '''
color str None
'''
        variables = {}
        super().__init__('foo', types, items_desc, variables)

    desc = _test_kiwi_options_shape()
    options = bcli_options(desc)
    self.assertEqual( None, options.color )

    class _test_kiwi_options_square(_test_kiwi_options_shape):
      def __init__(self):
        types = bcli_simple_type_item_list([
        ])
        items_desc = '''
color str None
'''
        variables = {}
        super().__init__('foo', types, items_desc, variables)

    desc = _test_kiwi_options_shape()
    options = bcli_options(desc)
    self.assertEqual( None, options.color )
    
  @classmethod
  def _make_test_options(clazz, **kwargs):
    types = bcli_simple_type_item_list([
    ])
    items_desc = '''
kiwi int ${bcli_foo}
pear int ${bcli_bar}
'''
    variables = {
      'bcli_foo': lambda: '42',
      'bcli_bar': lambda: '666',
    }
    desc = bcli_options_desc('foo', types, items_desc, variables)
    return bcli_options(desc, **kwargs)
    
if __name__ == '__main__':
  unit_test.main()
