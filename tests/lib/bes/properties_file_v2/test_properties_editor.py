#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file

from bes.testing.unit_test import unit_test
from bes.properties_file_v2.properties_editor import properties_editor as PE

class test_properties_editor_v2(unit_test):

  def test_set_value_non_existent_file(self):
    'Set the first value for a non existent properties file.'
    tmp = temp_file.make_temp_file()
    file_util.remove(tmp)
    e = PE(tmp)
    e.set_value('fruit', 'kiwi')
    expected = """fruit: kiwi\n"""
    self.assertMultiLineEqual(expected, file_util.read(tmp, codec = 'utf-8') )
    
  def test_set_value_empty_file(self):
    'Set the first value for a non existent properties file.'
    tmp = temp_file.make_temp_file(content = '')
    e = PE(tmp)
    e.set_value('fruit', 'kiwi')
    expected = """fruit: kiwi\n"""
    self.assertMultiLineEqual(expected, file_util.read(tmp, codec = 'utf-8') )
    
  def test_replace_value(self):
    'Set the first value for a non existent properties file.'
    tmp = temp_file.make_temp_file(content = '')
    e = PE(tmp)
    e.set_value('fruit', 'kiwi')
    expected = """fruit: kiwi\n"""
    self.assertMultiLineEqual(expected, file_util.read(tmp, codec = 'utf-8') )

    e.set_value('fruit', 'orange')
    expected = """fruit: orange\n"""
    self.assertMultiLineEqual(expected, file_util.read(tmp, codec = 'utf-8') )
    
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
    self.assertMultiLineEqual(expected, file_util.read(tmp, codec = 'utf-8') )
    
  def test_set_value_existing_file(self):
    'Add a second property to an existing property file.'
    content = """\
fruit: 'kiwi'
"""
    tmp = temp_file.make_temp_file(content = content)
    e = PE(tmp)
    self.assertMultiLineEqual(content, file_util.read(tmp, codec = 'utf-8') )
    e.set_value('status', 'doomed')
    expected = """\
fruit: kiwi
status: doomed
"""
    self.assertMultiLineEqual(expected, file_util.read(tmp, codec = 'utf-8') )

  def test_keys(self):
    'Get all the keys.'
    content = """\
fruit: kiwi
"""
    tmp = temp_file.make_temp_file(content = content)
    e = PE(tmp)
    self.assertEqual( [ 'fruit' ], e.keys() )

  def test_get_value(self):
    content = """\
color: 'green'
fruit: 'kiwi'
"""
    tmp = temp_file.make_temp_file(content = content)
    e = PE(tmp)
    self.assertEqual( 'green', e.get_value('color') )
    self.assertEqual( 'kiwi', e.get_value('fruit') )
    
  def test_remove_value(self):
    content = """\
color: 'green'
fruit: 'kiwi'
"""
    tmp = temp_file.make_temp_file(content = content)
    e = PE(tmp)
    self.assertEqual( 'green', e.get_value('color') )
    e.remove_value('color')
    with self.assertRaises(KeyError) as ctx:
      e.get_value('color')
    
  def test_values(self):
    content = """\
color: 'green'
fruit: 'kiwi'
"""
    tmp = temp_file.make_temp_file(content = content)
    e = PE(tmp)
    self.assertEqual( { 'color': 'green', 'fruit': 'kiwi' }, e.values() )
    
  def test_bump_version(self):
    content = """\
version: 1.2.3
"""
    tmp = temp_file.make_temp_file(content = content)
    e = PE(tmp)
    e.bump_version('version', 'major')
    self.assertEqual( '2.2.3', e.get_value('version') )
    
  def test_change_version(self):
    content = """\
version: 1.2.3
"""
    tmp = temp_file.make_temp_file(content = content)
    e = PE(tmp)
    e.change_version('version', 'major', 9)
    self.assertEqual( '9.2.3', e.get_value('version') )
    
if __name__ == '__main__':
  unit_test.main()
