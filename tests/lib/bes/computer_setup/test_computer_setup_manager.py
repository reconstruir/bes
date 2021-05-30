#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.computer_setup.computer_setup_manager import computer_setup_manager
from bes.computer_setup.computer_setup_task import computer_setup_task
from bes.computer_setup.computer_setup_options import computer_setup_options
from bes.computer_setup.computer_setup_error import computer_setup_error

from bes.common.check import check

class _test_tesk1(computer_setup_task):
  
  #@abstractmethod
  def name(self):
    return 'test1'

  #@abstractmethod
  def description(self):
    return 'test1'

  #@abstractmethod
  def average_duration(self):
    return 1.0

  #@abstractmethod
  def is_needed(self, options, values):
    'Return True of the task needs to run.'
    check.check_computer_setup_options(options)
    check.check_dict(values)

    assert '_db' in values
    db = values['_db']
    if not 'name' in values:
      raise computer_setup_error('Value not found: "name"')
    actual_name = db.get('name', None)
    expected_name = values.get('name')
    return actual_name != expected_name
  
  #@abstractmethod
  def run(self, options, values):
    'Run the task.'
    check.check_computer_setup_options(options)
    check.check_dict(values)

    assert '_db' in values
    db = values['_db']
    if not 'name' in values:
      raise computer_setup_error('Value not found: "name"')
    db['name'] = values.get('name')

class test_computer_setup_manager(unit_test):

  def test_is_needed_true(self):
    setup_content = '''\
task change_computer_name
  class: _test_tesk1
  system: macos
  value: fruit=kiwi
'''
    setup = self.make_temp_file(content = setup_content, suffix = '.cst')
    options = computer_setup_options()
    csm = computer_setup_manager(options = options)
    csm.add_tasks_from_config(setup)
    db = {}
    task_values = { 'name': 'lemon', '_db': db }
    self.assertTrue( csm.is_needed(task_values) )

  def test_is_needed_false(self):
    setup_content = '''\
task change_computer_name
  class: _test_tesk1
  system: macos
  value: fruit=kiwi
'''
    setup = self.make_temp_file(content = setup_content, suffix = '.cst')
    options = computer_setup_options()
    csm = computer_setup_manager(options = options)
    csm.add_tasks_from_config(setup)
    db = { 'name': 'lemon' }
    task_values = { 'name': 'lemon', '_db': db }
    self.assertFalse( csm.is_needed(task_values) )
    
  def test_run(self):
    setup_content = '''\
task change_computer_name
  class: _test_tesk1
  system: macos
  value: fruit=kiwi
'''
    setup = self.make_temp_file(content = setup_content, suffix = '.cst')
    options = computer_setup_options()
    csm = computer_setup_manager(options = options)
    csm.add_tasks_from_config(setup)
    db = {}
    task_values = { 'name': 'lemon', '_db': db }
    self.assertTrue( csm.is_needed(task_values) )
    csm.run(task_values)
    self.assertFalse( csm.is_needed(task_values) )
    
if __name__ == '__main__':
  unit_test.main()
