#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import typing
from datetime import datetime
#from datetime import timedelta

from bes.testing.unit_test import unit_test
from bes.bcli.bcli_options_desc import bcli_options_desc
from bes.bcli.bcli_option_desc_item import bcli_option_desc_item

class test_bcli_options_desc(unit_test):

  class _unit_test_kiwi_options_desc(bcli_options_desc):

    def __init__(self):
      super().__init__()

    #@abstractmethod
    def _types(self):
      return []

    #@abstractmethod
    def _options_desc(self):
      return '''
kiwi int default=${_var_foo}
pear int default=${_var_bar}
  '''
  
    #@abstractmethod
    def _variables(self):
      return {
        '_var_foo': lambda: '42',
        '_var_bar': lambda: '666',
      }

  def test___init__(self):
    desc = self._unit_test_kiwi_options_desc()
    self.assertEqual( [], desc.types )
    self.assertEqual( True, desc.has_option('kiwi') )
    self.assertEqual( True, desc.has_option('pear') )
    self.assertEqual( False, desc.has_option('notthere') )
    self.assertEqual( 42, desc.default('kiwi') )
    self.assertEqual( 666, desc.default('pear') )

    self.assertEqual( True, desc.check_value_type('kiwi', 13, None) )
    self.assertEqual( False, desc.check_value_type('kiwi', '13', None) )

    self.assertEqual( {
      'kiwi': bcli_option_desc_item('kiwi', 'int', int, 42, False),
      'pear': bcli_option_desc_item('pear', 'int', int, 666, False),
    }, desc.items_dict )

  def test_keys(self):
    desc = self._unit_test_kiwi_options_desc()
    self.assertEqual( ( 'kiwi', 'pear' ), desc.keys() )
    
if __name__ == '__main__':
  unit_test.main()
