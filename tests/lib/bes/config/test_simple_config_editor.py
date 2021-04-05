#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file

from bes.testing.unit_test import unit_test
from bes.config.simple_config_editor import simple_config_editor as SCE

class test_simple_config_file_editor(unit_test):

  def test_set_value_non_existent_file(self):
    'Set the first value for a non existent config file.'
    tmp = temp_file.make_temp_file()
    file_util.remove(tmp)
    e = SCE(tmp)
    e.set_value('something', 'fruit', 'kiwi')
    expected = '''\
something
  fruit: kiwi
'''
    self.assert_text_file_equal( expected, tmp, native_line_breaks = True )

  def test_replace_value(self):
    'Set the first value for a non existent config file.'
    tmp = temp_file.make_temp_file()
    file_util.remove(tmp)
    e = SCE(tmp)
    e.set_value('something', 'fruit', 'kiwi')
    expected = '''\
something
  fruit: kiwi
'''
    self.assert_text_file_equal( expected, tmp, native_line_breaks = True )
    e.set_value('something', 'fruit', 'apple')
    expected = '''\
something
  fruit: apple
'''
    self.assert_text_file_equal( expected, tmp, native_line_breaks = True )
    
  def test_get_value_existing_file(self):
    content = '''\
something
  fruit: kiwi
'''
    tmp = temp_file.make_temp_file(content = content)
    e = SCE(tmp)
    self.assert_text_file_equal(content, tmp, native_line_breaks = True )
    self.assertEqual( 'kiwi', e.get_value('something', 'fruit') )
    
  def test_get_value_missing_key(self):
    content = '''\
something
  fruit: kiwi
'''
    tmp = temp_file.make_temp_file(content = content)
    e = SCE(tmp)
    self.assert_text_file_equal(content, tmp, native_line_breaks = True )
    with self.assertRaises(KeyError) as ctx:
      self.assertEqual( None, e.get_value('something', 'color') )
    
  def test_import_file(self):
    content1 = '''\
something
  fruit: kiwi
'''
    content2 = '''\
something
  cheese: brie
'''
    content3 = '''\
something
  wine: barolo
'''
    tmp = temp_file.make_temp_file()
    e = SCE(tmp)
    e.import_file(temp_file.make_temp_file(content = content1))
    e.import_file(temp_file.make_temp_file(content = content2))
    e.import_file(temp_file.make_temp_file(content = content3))

    expected = '''\
something
  fruit: kiwi
  cheese: brie
  wine: barolo
'''
    self.assert_text_file_equal(expected, tmp, native_line_breaks = True )

  def test_import_file_empty_config(self):
    content1 = '''\
something
  fruit: kiwi
'''
    content2 = '''\
something
  cheese: brie
'''
    content3 = '''\
something
  wine: barolo
'''
    content4 = '''\
'''
    tmp = temp_file.make_temp_file()
    e = SCE(tmp)
    e.import_file(temp_file.make_temp_file(content = content1))
    e.import_file(temp_file.make_temp_file(content = content2))
    e.import_file(temp_file.make_temp_file(content = content3))
    e.import_file(temp_file.make_temp_file(content = content4))

    expected = '''\
something
  fruit: kiwi
  cheese: brie
  wine: barolo
'''
    self.assert_text_file_equal(expected, tmp, native_line_breaks = True )

  def test_import_file_empty_config(self):
    content = '''\
something
  fruit: kiwi
'''
    content2 = '''\
'''
    tmp = temp_file.make_temp_file(content = content)
    e = SCE(tmp)
    e.import_file(temp_file.make_temp_file(content = content2))

    expected = '''\
something
  fruit: kiwi
'''
    self.assert_text_file_equal(expected, tmp, native_line_breaks = True )
    
  def test_import_file_clobber(self):
    content1 = '''\
something
  fruit: kiwi
'''
    content2 = '''\
something
  cheese: brie
'''
    content3 = '''\
something
  fruit: lemon
'''
    tmp = temp_file.make_temp_file()
    e = SCE(tmp)
    e.import_file(temp_file.make_temp_file(content = content1))
    e.import_file(temp_file.make_temp_file(content = content2))
    e.import_file(temp_file.make_temp_file(content = content3))

    expected = '''\
something
  fruit: lemon
  cheese: brie
'''
    self.assert_text_file_equal(expected, tmp, native_line_breaks = True )

  def test_immediate_read(self):
    content = '''\
something
  fruit: kiwi
  cheese: brie
  wine: barolo
'''
    tmp = temp_file.make_temp_file(content = content)
    e = SCE(tmp)
    expected = '''\
something
  fruit: kiwi
  cheese: brie
  wine: barolo
'''
    
    self.assert_text_file_equal(expected, tmp, native_line_breaks = True )
    
if __name__ == '__main__':
  unit_test.main()
