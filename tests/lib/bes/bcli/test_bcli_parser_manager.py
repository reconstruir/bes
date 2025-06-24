#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from argparse import Namespace

from bes.system.check import check
from bes.testing.unit_test import unit_test

from bes.bcli.bcli_parser_manager import bcli_parser_manager
from bes.bcli.bcli_parser_maker_i import bcli_parser_maker_i

class test_bcli_parser_manager(unit_test):

  class _house_kitchen_parser_maker(bcli_parser_maker_i):
    
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
      pass
      
  def test_register_parser(self):
    m = bcli_parser_manager()
    m.register_parser([ 'house', 'kitchen' ], self._house_kitchen_parser_maker)
    p = m.find_parser_factory([ 'house', 'kitchen' ])
    self.assertEqual( self._house_kitchen_parser_maker,
                      m.find_parser_factory([ 'house', 'kitchen' ]) )

  def xtest__split_path_and_args(self):
    f = bcli_parser_manager._split_path_and_args

    self.assertEqual( ( [ 'house', 'kitchen' ], 'cook fish --method grill' ),
                      f('house kitchen cook fish --method grill') )
    return
    self.assertEqual( ( [ ], '--verbose --dry-run' ),
                      f('--verbose --dry-run') )
    self.assertEqual( ( [ 'house', 'kitchen' ], '' ),
                      f('fruit kiwi') )

  def test_parse_args(self):
    m = bcli_parser_manager()
    m.register_parser([ 'house', 'kitchen' ], self._house_kitchen_parser_maker)
    r = m.parse_args('house kitchen cook food --method grill')
    self.assertEqual( Namespace(what = 'food', method = 'grill'), r )

  def test_format_help(self):
    m = bcli_parser_manager()
    m.register_parser([ 'house', 'kitchen' ], self._house_kitchen_parser_maker)
    h = m.format_help('house kitchen cook food --help --method grill')

    expected = '''
usage: pytest [-h] {cook,clean} ...

positional arguments:
  {cook,clean}
    cook        Cook some food.
    clean       Clean the kitchen.

options:
  -h, --help    show this help message and exit
'''
    self.assert_string_equal_fuzzy(expected, h )
    
if __name__ == '__main__':
  unit_test.main()
