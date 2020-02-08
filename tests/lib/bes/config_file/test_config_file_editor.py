#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file

from bes.testing.unit_test import unit_test
from bes.config_file.config_file_editor import config_file_editor as CFE

class test_config_file_editor(unit_test):

  def test_set_value_non_existent_file(self):
    'Set the first value for a non existent config file.'
    tmp = temp_file.make_temp_file()
    file_util.remove(tmp)
    e = CFE(tmp)
    e.set_value('something', 'fruit', 'kiwi')
    expected = '''\
[something]
fruit = kiwi
'''
    self.assertMultiLineEqual(expected, file_util.read(tmp, codec = 'utf-8') )

  def test_set_value_non_existent_file_quoted(self):
    'Set the first value for a non existent config file.'
    tmp = temp_file.make_temp_file()
    file_util.remove(tmp)
    e = CFE(tmp, string_quote_char = '"')
    e.set_value('something', 'fruit', 'kiwi')
    expected = '''\
[something]
fruit = "kiwi"
'''
    self.assertMultiLineEqual(expected, file_util.read(tmp, codec = 'utf-8') )
    
  def test_replace_value(self):
    'Set the first value for a non existent config file.'
    tmp = temp_file.make_temp_file()
    file_util.remove(tmp)
    e = CFE(tmp)
    e.set_value('something', 'fruit', 'kiwi')
    expected = '''\
[something]
fruit = kiwi
'''
    self.assertMultiLineEqual(expected, file_util.read(tmp, codec = 'utf-8') )
    e.set_value('something', 'fruit', 'apple')
    expected = '''\
[something]
fruit = apple
'''
    self.assertMultiLineEqual(expected, file_util.read(tmp, codec = 'utf-8') )
    
  def test_replace_value_quoted(self):
    'Set the first value for a non existent config file.'
    tmp = temp_file.make_temp_file()
    file_util.remove(tmp)
    e = CFE(tmp, string_quote_char = '"')
    e.set_value('something', 'fruit', 'kiwi')
    expected = '''\
[something]
fruit = "kiwi"
'''
    self.assertMultiLineEqual(expected, file_util.read(tmp, codec = 'utf-8') )
    e.set_value('something', 'fruit', 'apple')
    expected = '''\
[something]
fruit = "apple"
'''
    self.assertMultiLineEqual(expected, file_util.read(tmp, codec = 'utf-8') )
    
  def test_get_value_existing_file(self):
    content = '''\
[something]
fruit = kiwi
'''
    tmp = temp_file.make_temp_file(content = content)
    e = CFE(tmp)
    self.assertMultiLineEqual(content, file_util.read(tmp, codec = 'utf-8') )
    self.assertEqual( 'kiwi', e.get_value('something', 'fruit') )
    
  def test_bump_version(self):
    content = '''\
[something]
ver = 1.2.3
'''
    e = CFE(temp_file.make_temp_file(content = content))
    self.assertEqual( '1.2.3', e.get_value('something', 'ver') )
    e.bump_version('something', 'ver', 'revision')
    self.assertEqual( '1.2.4', e.get_value('something', 'ver') )
    e.bump_version('something', 'ver', 'major')
    self.assertEqual( '2.2.4', e.get_value('something', 'ver') )
    e.bump_version('something', 'ver', 'major', reset_lower = True)
    self.assertEqual( '3.0.0', e.get_value('something', 'ver') )
    e.bump_version('something', 'ver', 'minor')
    self.assertEqual( '3.1.0', e.get_value('something', 'ver') )
    
  def test_change_version(self):
    content = '''\
[something]
ver = 1.2.3
'''
    e = CFE(temp_file.make_temp_file(content = content))
    self.assertEqual( '1.2.3', e.get_value('something', 'ver') )
    e.change_version('something', 'ver', 'major', 9)
    self.assertEqual( '9.2.3', e.get_value('something', 'ver') )
    e.change_version('something', 'ver', 'minor', 6)
    self.assertEqual( '9.6.3', e.get_value('something', 'ver') )
    e.change_version('something', 'ver', 'revision', 8)
    self.assertEqual( '9.6.8', e.get_value('something', 'ver') )

  def test_get_value_missing_key(self):
    content = '''\
[something]
fruit = kiwi
'''
    tmp = temp_file.make_temp_file(content = content)
    e = CFE(tmp)
    self.assertMultiLineEqual(content, file_util.read(tmp, codec = 'utf-8') )
    with self.assertRaises(KeyError) as ctx:
      self.assertEqual( None, e.get_value('something', 'color') )
    
  def test_import_file(self):
    content1 = '''\
[something]
fruit = kiwi
'''
    content2 = '''\
[something]
cheese = brie
'''
    content3 = '''\
[something]
wine = barolo
'''
    tmp = temp_file.make_temp_file()
    e = CFE(tmp)
    e.import_file(temp_file.make_temp_file(content = content1))
    e.import_file(temp_file.make_temp_file(content = content2))
    e.import_file(temp_file.make_temp_file(content = content3))

    expected = '''\
[something]
fruit = kiwi
cheese = brie
wine = barolo
'''
    self.assertMultiLineEqual(expected, file_util.read(tmp, codec = 'utf-8') )
    
  def test_import_file_clobber(self):
    content1 = '''\
[something]
fruit = kiwi
'''
    content2 = '''\
[something]
cheese = brie
'''
    content3 = '''\
[something]
fruit = lemon
'''
    tmp = temp_file.make_temp_file()
    e = CFE(tmp)
    e.import_file(temp_file.make_temp_file(content = content1))
    e.import_file(temp_file.make_temp_file(content = content2))
    e.import_file(temp_file.make_temp_file(content = content3))

    expected = '''\
[something]
fruit = lemon
cheese = brie
'''
    self.assertMultiLineEqual(expected, file_util.read(tmp, codec = 'utf-8') )
    
if __name__ == '__main__':
  unit_test.main()
