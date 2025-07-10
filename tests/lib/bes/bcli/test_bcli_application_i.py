#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from argparse import Namespace

from bes.system.check import check
from bes.testing.unit_test import unit_test

from bes.bcli.bcli_application import bcli_application

from _house_garage_command_factory import _house_garage_command_factory
from _house_kitchen_command_factory import _house_kitchen_command_factory
from _store_command_factory import _store_command_factory

class _test_app_2_levels(bcli_application):

  def __init__(self, unit_test):
    super().__init__()
    self._init_test = unit_test
    
  #@abstractmethod
  def name(self):
    return 'test'
  
  #@abstractmethod
  def parser_factories(self):
    return [
      _house_garage_command_factory,
      _house_kitchen_command_factory,
    ]

class _test_app_1_level(bcli_application):

  def __init__(self, unit_test):
    super().__init__()
    self._init_test = unit_test
  
  #@abstractmethod
  def name(self):
    return 'test'
  
  #@abstractmethod
  def parser_factories(self):
    return [
      _store_command_factory,
    ]

class test_bcli_appliction(unit_test):

  def test_run_2_levels(self):
    app = _test_app_2_levels(self)
    rv = app.run('house kitchen cook food --method grill')
    self.assertEqual( rv, 0 )

  def test_run_1_level(self):
    app = _test_app_1_level(self)
    rv = app.run('store buy bread')
    self.assertEqual( rv, 0 )

  def test_run_list_args(self):
    app = _test_app_1_level(self)
    rv = app.run([ 'store', 'buy', 'bread' ])
    self.assertEqual( rv, 0 )
    
if __name__ == '__main__':
  unit_test.main()


#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from argparse import Namespace

from bes.system.check import check
from bes.testing.unit_test import unit_test

from bes.bcli.bcli_application import bcli_application

from _house_garage_command_factory import _house_garage_command_factory
from _house_kitchen_command_factory import _house_kitchen_command_factory
from _store_command_factory import _store_command_factory

class _test_app_2_levels(bcli_application):

  def __init__(self, unit_test):
    super().__init__()
    self._init_test = unit_test
    
  #@abstractmethod
  def name(self):
    return 'test'
  
  #@abstractmethod
  def parser_factories(self):
    return [
      _house_garage_command_factory,
      _house_kitchen_command_factory,
    ]

class _test_app_1_level(bcli_application):

  def __init__(self, unit_test):
    super().__init__()
    self._init_test = unit_test
  
  #@abstractmethod
  def name(self):
    return 'test'
  
  #@abstractmethod
  def parser_factories(self):
    return [
      _store_command_factory,
    ]

class test_bcli_appliction(unit_test):

  def test_run_2_levels(self):
    app = _test_app_2_levels(self)
    rv = app.run('house kitchen cook food --method grill')
    self.assertEqual( rv, 0 )

  def test_run_1_level(self):
    app = _test_app_1_level(self)
    rv = app.run('store buy bread')
    self.assertEqual( rv, 0 )

  def test_run_list_args(self):
    app = _test_app_1_level(self)
    rv = app.run([ 'store', 'buy', 'bread' ])
    self.assertEqual( rv, 0 )
    
if __name__ == '__main__':
  unit_test.main()
  
