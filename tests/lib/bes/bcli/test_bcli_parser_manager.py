#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from argparse import Namespace

from bes.system.check import check
from bes.testing.unit_test import unit_test

from bes.bcli.bcli_parser_manager import bcli_parser_manager
from bes.bcli.bcli_parser_factory_i import bcli_parser_factory_i

class test_bcli_parser_manager(unit_test):

  class _house_kitchen_parser_factory(bcli_parser_factory_i):
    
    #@abstractmethod
    def has_sub_parsers(self):
      return True
  
    #@abstractmethod
    def add_sub_parsers(self, subparsers):
      p = subparsers.add_parser('cook', help = 'Cook some food.')
      p.add_argument('what', action = 'store', type = str,
                     help = 'What to cook')
      p.add_argument('--method', action = 'store', type = str, default = 'sear',
                     choices = ( 'sear', 'steam', 'grill' ),
                     help = 'Cooking method [ sear ]')

      p = subparsers.add_parser('clean', help = 'Clean the kitchen.')

    #@abstractmethod
    def add_arguments(self, parser):
      parser.add_argument('--output', action = 'store', type = str, default = 'json',
                          choices = ( 'json', 'text' ),
                          help = 'Output style [ json ]')

  class _house_garage_parser_factory(bcli_parser_factory_i):
    
    #@abstractmethod
    def has_sub_parsers(self):
      return True
  
    #@abstractmethod
    def add_sub_parsers(self, subparsers):
      p = subparsers.add_parser('clean', help = 'Clean the garage.')
      p.add_argument('--method', action = 'store', type = str, default = 'vacuum',
                     choices = ( 'vacuum', 'sweep' ),
                     help = 'Cleaning method [ vacuum ]')

      p = subparsers.add_parser('close', help = 'Close the garage.')

    #@abstractmethod
    def add_arguments(self, parser):
      parser.add_argument('--output', action = 'store', type = str, default = 'json',
                          choices = ( 'json', 'text' ),
                          help = 'Output style [ json ]')
      
  def test_register_one_factory(self):
    m = bcli_parser_manager()
    m.register_factory('house/kitchen', self._house_kitchen_parser_factory)
    p = m.find_factory('house/kitchen')
    self.assertEqual( self._house_kitchen_parser_factory,
                      m.find_factory('house/kitchen') )

  def test_register_two_factories(self):
    m = bcli_parser_manager()
    m.register_factory('house/kitchen', self._house_kitchen_parser_factory)
    m.register_factory('house/garage', self._house_garage_parser_factory)
    self.assertEqual( self._house_kitchen_parser_factory,
                      m.find_factory('house/kitchen') )
    self.assertEqual( self._house_garage_parser_factory,
                      m.find_factory('house/garage') )
    
  def xtest__split_path_and_args(self):
    f = bcli_parser_manager._split_path_and_args

    self.assertEqual( ( 'house/kitchen', 'cook fish --method grill' ),
                      f('house kitchen cook fish --method grill') )
    return
    self.assertEqual( ( [ ], '--verbose --dry-run' ),
                      f('--verbose --dry-run') )
    self.assertEqual( ( 'house/kitchen', '' ),
                      f('fruit kiwi') )

  def test_parse_args_one_factory(self):
    m = bcli_parser_manager()
    m.register_factory('house/kitchen', self._house_kitchen_parser_factory)

    self.assertEqual( Namespace(what = 'food', method = 'grill', output = 'json', __bcli_command__ = 'cook'),
                      m.parse_args('house kitchen cook food --method grill') )

  def test_parse_args_two_factories(self):
    m = bcli_parser_manager()
    m.register_factory('house/kitchen', self._house_kitchen_parser_factory)
    m.register_factory('house/garage', self._house_garage_parser_factory)

    self.assertEqual( Namespace(what = 'food', method = 'grill', output = 'json', __bcli_command__ = 'cook'),
                      m.parse_args('house kitchen cook food --method grill') )

    self.assertEqual( Namespace(method = 'sweep', output = 'json', __bcli_command__ = 'clean'),
                      m.parse_args('house garage clean --method sweep') )
    
  def test_format_help(self):
    m = bcli_parser_manager()
    m.register_factory('house/kitchen', self._house_kitchen_parser_factory)
    h = m.format_help('house kitchen cook food --help --method grill')

    expected = '''
usage: pytest [-h] [--output {json,text}] {cook,clean} ...

positional arguments:
  {cook,clean}  commands
    cook        Cook some food.
    clean       Clean the kitchen.

options:
  -h, --help    show this help message and exit
  --output {json,text} Output style [ json ]
'''
    self.assert_string_equal_fuzzy(expected, h )
    
if __name__ == '__main__':
  unit_test.main()
