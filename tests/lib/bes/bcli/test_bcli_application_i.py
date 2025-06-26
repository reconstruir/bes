#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from argparse import Namespace

from bes.system.check import check
from bes.testing.unit_test import unit_test

from bes.bcli.bcli_application_i import bcli_application_i

from _house_garage_parser_factory import _house_garage_parser_factory
from _house_kitchen_parser_factory import _house_kitchen_parser_factory

class _test_application(bcli_application_i):

  #@abstractmethod
  def name(self):
    return 'test'
  
  #@abstractmethod
  def parser_factories(self):
    return [
      _house_garage_parser_factory,
      _house_kitchen_parser_factory,
    ]

  def _command_house_kitchen_cook(self, method, output, what):
    print(f'_command_cook: method={method} output={output} what={what}')
    return 0
  
class test_bcli_appliction(unit_test):

  def test_run(self):
    app = _test_application()
    rv = app.run('house kitchen cook food --method grill')
    self.assertEqual( rv, 0 )
    
if __name__ == '__main__':
  unit_test.main()
