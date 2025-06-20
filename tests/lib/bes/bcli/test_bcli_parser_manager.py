#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.testing.unit_test import unit_test

from bes.bcli.bcli_parser_manager import bcli_parser_manager
from bes.bcli.bcli_parser_maker_i import bcli_parser_maker_i

class test_bcli_parser_manager(unit_test):

  class _house_kitchen_parser_maker(bcli_parser_maker_i):
    @classmethod
    #@abstractmethod
    def add_sub_parsers(clazz, subparsers):
      p = subparsers.add_parser('cook', help = 'Cook some food.')
      p.add_argument('what', action = 'store', type = str,
                     help = 'What to cook')
      p.add_argument('--method', action = 'store', type = str, default = 'sear',
                     choices = ( 'sear', 'steam', 'grill' ),
                     help = 'Cooking method [ sear ]')

      p = subparsers.add_parser('clean', help = 'Clean the kitchen.')
      
  def test_register_parser(self):
    m = bcli_parser_manager()
    m.register_parser([ 'house', 'kitchen' ], self._house_kitchen_parser_maker)
    p = m.find_parser([ 'house', 'kitchen' ])
    print(p)

  def test__split_path_and_args(self):
    f = bcli_parser_manager._split_path_and_args

    self.assertEqual( ( [ 'house', 'kitchen' ], 'cook fish --method grill' ),
                      f('house kitchen cook fish --method grill') )
    return
    self.assertEqual( ( [ ], '--verbose --dry-run' ),
                      f('--verbose --dry-run') )
    self.assertEqual( ( [ 'house', 'kitchen' ], '' ),
                      f('fruit kiwi') )

  def test_parse(self):
    m = bcli_parser_manager()
    m.register_parser([ 'house', 'kitchen' ], self._house_kitchen_parser_maker)
    r = m.parse('house kitchen cook food --method grill')
    print(r)

if __name__ == '__main__':
  unit_test.main()
