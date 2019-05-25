#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.testing.unit_test import unit_test
from bes.fs import file_util, temp_file

from bes.config_file.config import config

class test_config(unit_test):

  def test__make_parser_from_text(self):
    text = '''\
[default]
color = red
fruit = apple

[new_zealand]
color = green
fruit = kiwi

[indonesia]
color = yellow
fruit = durian

[antartica]
'''
    self.assert_dict_as_text_equal( {
      'default': {
        'color': 'red',
        'fruit': 'apple',
      },
      'new_zealand': {
        'color': 'green',
        'fruit': 'kiwi',
      },
      'indonesia': {
        'color': 'yellow',
        'fruit': 'durian',
      },
      'antartica': {
      },
    }, config._make_parser_from_text(text).to_dict() )

  def test__make_parser_from_file(self):
    text = '''\
[default]
color = red
fruit = apple

[new_zealand]
color = green
fruit = kiwi

[indonesia]
color = yellow
fruit = durian

[antartica]
'''
    self.assert_dict_as_text_equal( {
      'default': {
        'color': 'red',
        'fruit': 'apple',
      },
      'new_zealand': {
        'color': 'green',
        'fruit': 'kiwi',
      },
      'indonesia': {
        'color': 'yellow',
        'fruit': 'durian',
      },
      'antartica': {
      },
    }, config._make_parser_from_file(temp_file.make_temp_file(content = text)).to_dict() )

  def test___str__(self):
    text = '''\
[default]
color = red
fruit = apple

[new_zealand]
color = green
fruit = kiwi

[indonesia]
color = yellow
fruit = durian

[antartica]
'''
    self.assertMultiLineEqual( text, str(config.load_from_text(text, '<unittest>')) )
    
  def test_set_value(self):
    c = config()
    c.set_value('new_zealand', 'color', 'green')
    c.set_value('new_zealand', 'fruit', 'kiwi')
    expected = '''\
[new_zealand]
color = green
fruit = kiwi
'''
    self.assertMultiLineEqual( expected, str(c) )
    c.set_value('indonesia', 'color', 'yellow')
    c.set_value('indonesia', 'fruit', 'durian')
    expected = '''\
[new_zealand]
color = green
fruit = kiwi

[indonesia]
color = yellow
fruit = durian
'''

  def test_get_value(self):
    text = '''\
[default]
color = red
fruit = apple

[new_zealand]
color = green
fruit = kiwi

[indonesia]
color = yellow
fruit = durian

[antartica]
'''
    c = config.load_from_text(text, '<unittest>')
    self.assertEqual( 'red', c.get_value('default', 'color') )
    self.assertEqual( 'apple', c.get_value('default', 'fruit') )
    with self.assertRaises(ValueError) as ctx:
      c.get_value('default', 'notthere')

  def test_has_value(self):
    text = '''\
[default]
color = red
fruit = apple

[new_zealand]
color = green
fruit = kiwi

[indonesia]
color = yellow
fruit = durian

[antartica]
'''
    c = config.load_from_text(text, '<unittest>')
    self.assertTrue( c.has_value('default', 'color') )
    self.assertTrue( c.has_value('default', 'fruit') )
    self.assertFalse( c.has_value('default', 'notthere') )
      
  def test_save(self):
    text = '''\
[default]
color = red
fruit = apple

[new_zealand]
color = green
fruit = kiwi

[indonesia]
color = yellow
fruit = durian

[antartica]
'''
    c = config.load_from_text(text, '<unittest>')
    tmp = temp_file.make_temp_file()
    c.save(tmp, codec = 'utf-8')
    self.assertMultiLineEqual( text, file_util.read(tmp, codec = 'utf-8') )

  def test_bump_version(self):
    c = config.load_from_text('[something]\nversion = 1.2.3\n', '<unittest>')
    self.assertEqual( '1.2.3', c.get_value('something', 'version') )
    c.bump_version('something', 'version', config.REVISION)
    self.assertEqual( '1.2.4', c.get_value('something', 'version') )
    c.bump_version('something', 'version', config.MAJOR)
    self.assertEqual( '2.2.4', c.get_value('something', 'version') )
    c.bump_version('something', 'version', config.MAJOR)
    self.assertEqual( '3.2.4', c.get_value('something', 'version') )
    
  def test_change_version(self):
    c = config.load_from_text('[something]\nversion = 1.2.3\n', '<unittest>')
    self.assertEqual( '1.2.3', c.get_value('something', 'version') )
    c.change_version('something', 'version', config.MAJOR, 9)
    self.assertEqual( '9.2.3', c.get_value('something', 'version') )
    c.change_version('something', 'version', config.MINOR, 6)
    self.assertEqual( '9.6.3', c.get_value('something', 'version') )
    c.change_version('something', 'version', config.REVISION, 8)
    self.assertEqual( '9.6.8', c.get_value('something', 'version') )
    
if __name__ == '__main__':
  unit_test.main()
