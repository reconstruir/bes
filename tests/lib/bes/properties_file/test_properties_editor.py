#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.fs import file_util, temp_file

from bes.testing.unit_test import unit_test
from bes.properties_file.properties_editor import properties_editor as PE

class test_properties_editor(unit_test):

  def test_set_value_non_existent_file(self):
    'Set the first value for a non existent properties file.'
    tmp = temp_file.make_temp_file()
    file_util.remove(tmp)
    e = PE(tmp)
    e.set_value('fruit', 'kiwi')
    expected = """fruit: kiwi\n"""
    self.assertMultiLineEqual(expected, file_util.read(tmp) )
    
  def test_set_value_empty_file(self):
    'Set the first value for a non existent properties file.'
    tmp = temp_file.make_temp_file(content = '')
    e = PE(tmp)
    e.set_value('fruit', 'kiwi')
    expected = """fruit: kiwi\n"""
    self.assertMultiLineEqual(expected, file_util.read(tmp) )
    
  def test_replace_value(self):
    'Set the first value for a non existent properties file.'
    tmp = temp_file.make_temp_file(content = '')
    e = PE(tmp)
    e.set_value('fruit', 'kiwi')
    expected = """fruit: kiwi\n"""
    self.assertMultiLineEqual(expected, file_util.read(tmp) )

    e.set_value('fruit', 'orange')
    expected = """fruit: orange\n"""
    self.assertMultiLineEqual(expected, file_util.read(tmp) )
    
  def test_set_value_many_values(self):
    'Set the first value for a non existent properties file.'
    tmp = temp_file.make_temp_file(content = '')
    e = PE(tmp)
    e.set_value('fruit', 'kiwi')
    e.set_value('version', '1.2.3')
    e.set_value('status', 'doomed')
    expected = """\
fruit: kiwi
status: doomed
version: 1.2.3
"""
    self.assertMultiLineEqual(expected, file_util.read(tmp) )
    
  def test_set_value_existing_file(self):
    'Add a second property to an existing property file.'
    content = """\
fruit: 'kiwi'
"""
    tmp = temp_file.make_temp_file(content = content)
    e = PE(tmp)
    self.assertMultiLineEqual(content, file_util.read(tmp) )
    e.set_value('status', 'doomed')
    expected = """\
fruit: kiwi
status: doomed
"""
    self.assertMultiLineEqual(expected, file_util.read(tmp) )

  def test_keys(self):
    'Get all the keys.'
    content = """\
fruit: kiwi
"""
    tmp = temp_file.make_temp_file(content = content)
    e = PE(tmp)
    self.assertEqual( [ 'fruit' ], e.keys() )
    
if __name__ == '__main__':
  unit_test.main()
