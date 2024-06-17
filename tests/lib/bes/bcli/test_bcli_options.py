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

  def test_keys(self):
    options = self._make_test_options()
    self.assertEqual( ( 'kiwi', 'pear' ), options.keys() )
      
  def xtest___str__(self):
    options = self._make_test_options()
    self.assertEqual( '''
''', str(options) )
      
  class _test_kiwi_options_shape(bcli_options_desc):

    def __init__(self):
      super().__init__()

    #@abstractmethod
    def name(self):
      return '_test_kiwi_options_shape'
  
    #@abstractmethod
    def types(self):
      return bcli_simple_type_item_list([
      ])

    #@abstractmethod
    def options_desc(self):
      return '''
color str None
  '''
  
    #@abstractmethod
    def variables(self):
      return {
        '_var_shape_foo': lambda: '42',
        '_var_shape_bar': lambda: '666',
      }

  class _test_kiwi_options_square(_test_kiwi_options_shape):

    def __init__(self):
      super().__init__()

    #@abstractmethod
    def name(self):
      return '_test_kiwi_options_square'
  
    #@abstractmethod
    def types(self):
      return super().types() + bcli_simple_type_item_list([
      ])

    #@abstractmethod
    def options_desc(self):
      return self.combine_options_desc(super().options_desc(), '''
size int 0
''')
  
    #@abstractmethod
    def variables(self):
      return self.combine_variables(super().variables(), {
        '_var_square_foo': lambda: '42',
        '_var_square_bar': lambda: '666',
      })
    
  def test_subclass(self):
    shape_desc = self._test_kiwi_options_shape()
    shape_options = bcli_options(shape_desc)

    square_desc = self._test_kiwi_options_square()
    square_options = bcli_options(square_desc,
                                  color = 'blue',
                                  size = 42)
    self.assertEqual( [
      '_var_shape_foo',
      '_var_shape_bar',
    ], list(shape_desc.variables().keys()) )
    
    self.assertEqual( None, shape_options.color )
    self.assertEqual( False, shape_desc.has_option('size') )
    
    self.assertEqual( [
      '_var_shape_foo',
      '_var_shape_bar',
      '_var_square_foo',
      '_var_square_bar',
    ], list(square_desc.variables().keys()) )
    self.assertEqual( True, square_desc.has_option('size') )
    self.assertEqual( 'blue', square_options.color )
    self.assertEqual( 42, square_options.size )

  class _unit_test_kiwi_options_desc(bcli_options_desc):

    def __init__(self):
      super().__init__()

    #@abstractmethod
    def name(self):
      return '_kiwi_options_desc'
  
    #@abstractmethod
    def types(self):
      return bcli_simple_type_item_list([
      ])

    #@abstractmethod
    def options_desc(self):
      return '''
kiwi int ${_var_foo} # default=${_var_foo} secret=True
pear int ${_var_bar}
  '''
  
    #@abstractmethod
    def variables(self):
      return {
        '_var_foo': lambda: '42',
        '_var_bar': lambda: '666',
      }
    
  @classmethod
  def _make_test_options(clazz, **kwargs):
    desc = clazz._unit_test_kiwi_options_desc()
    return bcli_options(desc, **kwargs)
    
if __name__ == '__main__':
  unit_test.main()
