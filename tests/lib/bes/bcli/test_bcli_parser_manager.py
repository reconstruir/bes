#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from argparse import Namespace

from bes.system.check import check
from bes.testing.unit_test import unit_test

from bes.bcli.bcli_parser_manager import bcli_parser_manager
from bes.bcli.bcli_command_factory_i import bcli_command_factory_i

from _house_garage_parser_factory import _house_garage_parser_factory
from _house_kitchen_parser_factory import _house_kitchen_parser_factory
from _store_parser_factory import _store_parser_factory

class test_bcli_parser_manager(unit_test):

  def test_register_one_factory(self):
    m = bcli_parser_manager()
    m.register_factory(_house_kitchen_parser_factory)
    self.assertEqual( _house_kitchen_parser_factory,
                      m.find_factory('house/kitchen') )

  def test_register_two_factories(self):
    m = bcli_parser_manager()
    m.register_factory(_house_kitchen_parser_factory)
    m.register_factory(_house_garage_parser_factory)
    self.assertEqual( _house_kitchen_parser_factory,
                      m.find_factory('house/kitchen') )
    self.assertEqual( _house_garage_parser_factory,
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
    m.register_factory(_house_kitchen_parser_factory)

    self.assertEqual( Namespace(what = 'food', method = 'grill', output = 'json', __bcli_command_name__ = 'cook'),
                      m.parse_args('house kitchen cook food --method grill').ns )

  def test_parse_args_two_factories(self):
    m = bcli_parser_manager()
    m.register_factory(_house_kitchen_parser_factory)
    m.register_factory(_house_garage_parser_factory)

    self.assertEqual( Namespace(what = 'food', method = 'grill', output = 'json', __bcli_command_name__ = 'cook'),
                      m.parse_args('house kitchen cook food --method grill').ns )

    self.assertEqual( Namespace(method = 'sweep', output = 'json', __bcli_command_name__ = 'clean'),
                      m.parse_args('house garage clean --method sweep').ns )
    
  def test_format_help(self):
    m = bcli_parser_manager()
    m.register_factory(_house_kitchen_parser_factory)
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

  def test_one_level_path(self):
    m = bcli_parser_manager()
    m.register_factory(_store_parser_factory)
    self.assertEqual( _store_parser_factory,
                      m.find_factory('store') )
    
if __name__ == '__main__':
  unit_test.main()
