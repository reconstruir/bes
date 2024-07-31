#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import typing

from datetime import datetime
#from datetime import timedelta

from bes.testing.unit_test import unit_test

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

class test_bcli_options(unit_test):

  def test_to_dict_caca(self):
    options = self._make_test_options(password = 'foo')
    self.assertEqual( {
      'kiwi': 42,
      'pear': 666,
      'password': '*************',
    }, options.to_dict() )

  def test_to_dict_without_hiding_secrets(self):
    options = self._make_test_options(password = 'foo')
    self.assertEqual( {
      'kiwi': 42,
      'pear': 666,
      'password': 'foo',
    }, options.to_dict(hide_secrets = False) )
    
  def test___str__(self):
    options = self._make_test_options(password = 'foo')
    self.assertEqual( '''{'kiwi': 42, 'password': '*************', 'pear': 666}''', str(options) )

  def test_to_str_without_hiding_secrets(self):
    options = self._make_test_options(password = 'foo')
    self.assertEqual( '''{'kiwi': 42, 'password': 'foo', 'pear': 666}''', options.to_str(hide_secrets = False) )
    
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
    self.assertEqual( ( 'kiwi', 'password', 'pear' ), options.keys() )
      
  class _test_kiwi_options_shape(bcli_options_desc):

    def __init__(self):
      super().__init__()

    #@abstractmethod
    def name(self):
      return '_test_kiwi_options_shape'
  
    #@abstractmethod
    def types(self):
      return []

    #@abstractmethod
    def options_desc(self):
      return '''
color str
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
      return super().types() + []

    #@abstractmethod
    def options_desc(self):
      return self.combine_options_desc(super().options_desc(), '''
size int default=0
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

    d = shape_options.to_dict()
    import pprint
    print(pprint.pformat(d), flush = True)
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
      return []

    #@abstractmethod
    def options_desc(self):
      return '''
kiwi int default=${_var_foo}
pear int default=${_var_bar}
password str secret=True
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
