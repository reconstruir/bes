#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from bes.testing.unit_test import unit_test
from bes.config.simple_config import simple_config as SC
from bes.system.env_override import env_override
from bes.key_value.key_value_list import key_value_list as KVL

class test_simple_config(unit_test):

  def test_basic(self):
    text = '''\
# This is one
credential
  provider: pcloud
  type: download
  email: email1@bar.com # one
  password: sekret1

# This is two
credential
  provider: pcloud
  type: upload
  email: email2@bar.com # two
  password: sekret2
'''
    
    s = SC.from_text(text)

    with self.assertRaises(SC.error):
      s.find_sections('foo')

    sections = s.find_sections('credential')
    self.assertEqual( 2, len(sections) )
    self.assertEqual( 'credential', sections[0].header.name )
    self.assertEqual( 'download', sections[0].find_by_key('type') )
    self.assertEqual( 'credential', sections[1].header.name )
    self.assertEqual( 'upload', sections[1].find_by_key('type') )
    self.assertEqual( {
      'provider': 'pcloud',
      'type': 'download',
      'email': 'email1@bar.com',
      'password': 'sekret1',
      }, sections[0].to_dict() )
    self.assertTrue( s.has_section('credential') )
    self.assertFalse( s.has_section('nothere') )
    
  def test_env_var(self):
    text = '''\
# This is one
credential
  provider: pcloud
  type: download
  email: email1@bar.com # one
  password: ${SEKRET1}

# This is two
credential
  provider: pcloud
  type: upload
  email: email2@bar.com # two
  password: ${SEKRET2}
'''
    with env_override(env = { 'SEKRET1': 'sekret1', 'SEKRET2': 'sekret2' }) as tmp_env:
      s = SC.from_text(text)

      sections = s.find_sections('credential')
      self.assertEqual( 2, len(sections) )
      self.assertEqual( 'download', sections[0].find_by_key('type') )
      self.assertEqual( 'upload', sections[1].find_by_key('type') )
      self.assertEqual( '${SEKRET1}', sections[0].find_by_key('password', resolve_env_vars = False) )
      self.assertEqual( 'sekret1', sections[0].find_by_key('password', resolve_env_vars = True) )
      self.assertEqual( 'sekret1', sections[0].get_value('password') )
      self.assertEqual( True, sections[0].has_key('password') )
      self.assertEqual( False, sections[0].has_key('missingkey') )

      self.assertEqual( {
        'provider': 'pcloud',
        'type': 'download',
        'email': 'email1@bar.com',
        'password': '${SEKRET1}',
      }, sections[0].to_dict(resolve_env_vars = False) )

      self.assertEqual( {
        'provider': 'pcloud',
        'type': 'download',
        'email': 'email1@bar.com',
        'password': 'sekret1',
      }, sections[0].to_dict(resolve_env_vars = True) )
    
  def test_env_var_missing(self):
    text = '''\
# This is one
credential
  provider: pcloud
  type: download
  email: email1@bar.com # one
  password: ${SEKRET1}
'''
    s = SC.from_text(text)
    sections = s.find_sections('credential')
    self.assertEqual( 1, len(sections) )
    with self.assertRaises(SC.error) as context:
      sections[0].to_dict(resolve_env_vars = True)

  def test_extends(self):
    text = '''\
fruit
  name: apple
  color: red

cheese
  name: brie
  type: creamy

foo extends fruit
  color: green
'''
    
    s = SC.from_text(text)

    sections = s.find_sections('foo')
    self.assertEqual( 1, len(sections) )
    self.assertEqual( 'foo', sections[0].header.name )
    self.assertEqual( 'fruit', sections[0].header.extends )
    self.assertEqual( 'green', sections[0].find_by_key('color') )
    self.assertEqual( {
      'color': 'green',
      }, sections[0].to_dict() )
      
  def test_extends_missing_base(self):
    text = '''\
foo extends
  color: green
'''
    
    with self.assertRaises(SC.error):
      SC.from_text(text)

  def test_annotation_key_only(self):
    text = '''\
fruit
  name: lemon
  tart: true
  is_good[annotation1,annotation2]: true

fruit
  name: apple
  tart: true
  is_good[annotation2]: true

fruit
  name: watermelon
  tart: false
  is_good[annotation1]: true

fruit
  name: strawberry
  tart: false
  is_good: true
'''
    
    s = SC.from_text(text)

    with self.assertRaises(SC.error):
      s.find_sections('foo')

    sections = s.find_sections('fruit')
    self.assertEqual( 4, len(sections) )
    
    self.assertEqual( 'fruit', sections[0].header.name )
    self.assertEqual( 'lemon', sections[0].find_by_key('name') )
    self.assertEqual( 'true', sections[0].find_by_key('tart') )
    self.assertEqual( 'true', sections[0].find_by_key('is_good') )
    self.assertEqual( KVL([ ( 'annotation1', None), ( 'annotation2', None ) ]),
                      sections[0].find_entry('is_good').annotations )

    self.assertEqual( 'fruit', sections[1].header.name )
    self.assertEqual( 'apple', sections[1].find_by_key('name') )
    self.assertEqual( 'true', sections[1].find_by_key('tart') )
    self.assertEqual( 'true', sections[1].find_by_key('is_good') )
    self.assertEqual( KVL([ ( 'annotation2', None ) ]),
                      sections[1].find_entry('is_good').annotations )
    
    self.assertEqual( 'fruit', sections[2].header.name )
    self.assertEqual( 'watermelon', sections[2].find_by_key('name') )
    self.assertEqual( 'false', sections[2].find_by_key('tart') )
    self.assertEqual( 'true', sections[2].find_by_key('is_good') )
    self.assertEqual( KVL([ ( 'annotation1', None ) ]),
                      sections[2].find_entry('is_good').annotations )
    
    self.assertEqual( 'fruit', sections[3].header.name )
    self.assertEqual( 'strawberry', sections[3].find_by_key('name') )
    self.assertEqual( 'false', sections[3].find_by_key('tart') )
    self.assertEqual( 'true', sections[3].find_by_key('is_good') )
    self.assertEqual( None, sections[3].find_entry('is_good').annotations )

if __name__ == '__main__':
  unit_test.main()
