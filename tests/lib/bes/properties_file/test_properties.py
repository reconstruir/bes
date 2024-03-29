#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.testing.unit_test import unit_test
from bes.properties_file.properties import properties as P

class test_properties(unit_test):

  def test_load_from_empty_yaml(self):
    text = ''
    a = P.from_yaml_text('', '<unitest>')
    self.assertEqual( [], a.keys() )
  
  def test_load_from_yaml(self):
    text = '''\
fruit: 'kiwi'
version: '1.2.3'
status: 'doomed'
'''
    a = P.from_yaml_text(text, '<unitest>')
    self.assertEqual( 'kiwi', a.get_value('fruit') )
    self.assertEqual( [ 'fruit', 'status', 'version' ], a.keys() )
    
  def test_to_yaml_text(self):
    a = P()
    a.set_value('fruit', 'kiwi')
    a.set_value('version', '1.2.3')
    a.set_value('status', 'doomed')
    
    expected = '''\
fruit: kiwi
status: doomed
version: 1.2.3
'''
    self.assertMultiLineEqual( expected, a.to_yaml_text() )
    
  def test_to_yaml_text_empty(self):
    a = P()
    self.assertMultiLineEqual( '', a.to_yaml_text() )

  def test_bump_version_non_existent(self):
    a = P()
    a.bump_version('version', P.REVISION)
    self.assertEqual( '1.0.0', a.get_value('version') )
    
  def test_bump_version_existing(self):
    a = P()
    a.set_value('version', '1.2.3')
    a.bump_version('version', P.REVISION)
    self.assertEqual( '1.2.4', a.get_value('version') )
    
  def test_bump_version_with_major_component(self):
    a = P()
    a.set_value('version', '1.2.3')
    a.bump_version('version', P.MAJOR )
    self.assertEqual( '2.2.3', a.get_value('version') )
    
  def test_bump_version_with_minor_component(self):
    a = P()
    a.set_value('version', '1.2.3')
    a.bump_version('version', P.MINOR )
    self.assertEqual( '1.3.3', a.get_value('version') )
    
  def test_properties(self):
    a = P()
    a.set_value('version', '1.2.3')
    a.set_value('status', 'doomed')
    a.set_value('fruit', 'kiwi')
    self.assertEqual( {
      'version': '1.2.3',
      'status': 'doomed',
      'fruit': 'kiwi',
    }, a.properties() )

  def test_items(self):
    a = P()
    a.set_value('version', '1.2.3')
    a.set_value('status', 'doomed')
    a.set_value('fruit', 'kiwi')
    self.assertEqual( [
      ( 'fruit', 'kiwi' ), 
      ( 'status', 'doomed' ), 
      ( 'version', '1.2.3' ), 
    ], a.items() )

  def test_load_from_empty_java(self):
    text = ''
    a = P.from_java_text('', '<unitest>')
    self.assertEqual( [], a.keys() )
  
  def test_load_from_java(self):
    text = '''\
fruit=kiwi
version=1.2.3
status=doomed
'''
    a = P.from_java_text(text, '<unitest>')
    self.assertEqual( 'kiwi', a.get_value('fruit') )
    self.assertEqual( [ 'fruit', 'status', 'version' ], a.keys() )
    
  def test_to_java_text(self):
    a = P()
    a.set_value('fruit', 'kiwi')
    a.set_value('version', '1.2.3')
    a.set_value('status', 'doomed')
    
    expected = '''\
fruit=kiwi
status=doomed
version=1.2.3
'''
    self.assertMultiLineEqual( expected, a.to_java_text() )
    
  def test_to_java_text_empty(self):
    a = P()
    self.assertMultiLineEqual( '', a.to_java_text() )

  def test_change_version(self):
    a = P.from_yaml_text('version: 1.2.3\n', '<unitest>')
    self.assertEqual( '1.2.3', a.get_value('version') )
    a.change_version('version', P.MAJOR, 9)
    self.assertEqual( '9.2.3', a.get_value('version') )
    a.change_version('version', P.MINOR, 6)
    self.assertEqual( '9.6.3', a.get_value('version') )
    a.change_version('version', P.REVISION, 8)
    self.assertEqual( '9.6.8', a.get_value('version') )
    
if __name__ == '__main__':
  unit_test.main()
