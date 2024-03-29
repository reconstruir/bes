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
    tmp = self.make_temp_file(prefix = 'set_value_non_existent_file')
    file_util.remove(tmp)
    e = PE(tmp)
    e.set_value('fruit', 'kiwi')
    expected = """fruit: kiwi\n"""
    self.assert_text_file_equal( expected, tmp )
    
  def test_set_value_empty_file(self):
    'Set the first value for a non existent properties file.'
    tmp = self.make_temp_file(prefix = 'set_value_empty_file', content = '')
    e = PE(tmp)
    e.set_value('fruit', 'kiwi')
    expected = """fruit: kiwi\n"""
    self.assert_text_file_equal( expected, tmp )
    
  def test_replace_value(self):
    'Set the first value for a non existent properties file.'
    tmp = self.make_temp_file(content = '', prefix = 'replace_value')
    e = PE(tmp)
    e.set_value('fruit', 'kiwi')
    expected = """fruit: kiwi\n"""
    self.assert_text_file_equal( expected, tmp )

    e.set_value('fruit', 'orange')
    expected = """fruit: orange\n"""
    self.assert_text_file_equal( expected, tmp )
    
  def test_set_value_many_values(self):
    'Set the first value for a non existent properties file.'
    tmp = self.make_temp_file(content = '', prefix = 'set_value_many_values')
    e = PE(tmp)
    e.set_value('fruit', 'kiwi')
    e.set_value('version', '1.2.3')
    e.set_value('status', 'doomed')
    expected = """\
fruit: kiwi
status: doomed
version: 1.2.3
"""
    self.assert_text_file_equal( expected, tmp )
    
  def test_set_value_existing_file(self):
    'Add a second property to an existing property file.'
    content = """\
fruit: 'kiwi'
"""
    tmp = self.make_temp_file(content = content, prefix = 'set_value_existing_file')
    e = PE(tmp)
    self.assert_text_file_equal( content, tmp )
    e.set_value('status', 'doomed')
    expected = """\
fruit: kiwi
status: doomed
"""
    self.assert_text_file_equal( expected, tmp )

  def test_keys(self):
    'Get all the keys.'
    content = """\
fruit: kiwi
"""
    tmp = self.make_temp_file(content = content, prefix = 'keys')
    e = PE(tmp)
    self.assertEqual( [ 'fruit' ], e.keys() )

  def test_get_value(self):
    content = """\
color: 'green'
fruit: 'kiwi'
"""
    tmp = self.make_temp_file(content = content, prefix = 'get_value')
    e = PE(tmp)
    self.assertEqual( 'green', e.get_value('color') )
    self.assertEqual( 'kiwi', e.get_value('fruit') )
    
  def test_remove_value(self):
    content = """\
color: 'green'
fruit: 'kiwi'
"""
    tmp = self.make_temp_file(content = content, prefix = 'remove_value')
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
    tmp = self.make_temp_file(content = content, prefix = 'values')
    e = PE(tmp)
    self.assertEqual( { 'color': 'green', 'fruit': 'kiwi' }, e.values() )
    
  def test_bump_version(self):
    content = """\
version: 1.2.3
"""
    tmp = self.make_temp_file(content = content, prefix = 'bump_version')
    e = PE(tmp)
    e.bump_version('version', 'major')
    self.assertEqual( '2.2.3', e.get_value('version') )
    
  def test_change_version(self):
    content = """\
version: 1.2.3
"""
    tmp = self.make_temp_file(content = content, prefix = 'change_version')
    e = PE(tmp)
    e.change_version('version', 'major', 9)
    self.assertEqual( '9.2.3', e.get_value('version') )

  def test_backup(self):
    'Set the first value for a non existent properties file.'
    tmp_dir = self.make_temp_dir(prefix = 'backup')
    tmp = file_util.save(path.join(tmp_dir, 'foo.props'), content = '')
    tmp_backup = tmp + '.bak'
    e = PE(tmp, backup = True)
    e.set_value('fruit', 'kiwi')
    self.assertFalse( path.isfile(tmp_backup) )
    expected = '''\
fruit: kiwi
'''
    self.assert_text_file_equal( expected, tmp )
    
    e.set_value('fruit', 'melon')
    self.assertTrue( path.isfile(tmp_backup) )
    self.assert_text_file_equal( expected, tmp_backup )
    
if __name__ == '__main__':
  unit_test.main()
