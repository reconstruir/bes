#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from bes.testing.unit_test import unit_test
from bes.config.simple_config import simple_config
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
    
    s = simple_config.from_text(text)

    with self.assertRaises(simple_config.error):
      s.find_sections('foo')

    sections = s.find_sections('credential')
    self.assertEqual( 2, len(sections) )
    self.assertEqual( 'credential', sections[0].header_.name )
    self.assertEqual( 'download', sections[0].find_by_key('type') )
    self.assertEqual( 'credential', sections[1].header_.name )
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
      s = simple_config.from_text(text)

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
    s = simple_config.from_text(text)
    sections = s.find_sections('credential')
    self.assertEqual( 1, len(sections) )
    with self.assertRaises(simple_config.error) as context:
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
    
    s = simple_config.from_text(text)

    sections = s.find_sections('foo')
    self.assertEqual( 1, len(sections) )
    self.assertEqual( 'foo', sections[0].header_.name )
    self.assertEqual( 'fruit', sections[0].header_.extends )
    self.assertEqual( 'green', sections[0].find_by_key('color') )
    self.assertEqual( {
      'color': 'green',
      }, sections[0].to_dict() )
      
  def test_extends_missing_base(self):
    text = '''\
foo extends
  color: green
'''
    
    with self.assertRaises(simple_config.error):
      simple_config.from_text(text)

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
    
    s = simple_config.from_text(text)

    with self.assertRaises(simple_config.error):
      s.find_sections('foo')

    sections = s.find_sections('fruit')
    self.assertEqual( 4, len(sections) )
    
    self.assertEqual( 'fruit', sections[0].header_.name )
    self.assertEqual( 'lemon', sections[0].find_by_key('name') )
    self.assertEqual( 'true', sections[0].find_by_key('tart') )
    self.assertEqual( 'true', sections[0].find_by_key('is_good') )
    self.assertEqual( KVL([ ( 'annotation1', None), ( 'annotation2', None ) ]),
                      sections[0].find_entry('is_good').annotations )

    self.assertEqual( 'fruit', sections[1].header_.name )
    self.assertEqual( 'apple', sections[1].find_by_key('name') )
    self.assertEqual( 'true', sections[1].find_by_key('tart') )
    self.assertEqual( 'true', sections[1].find_by_key('is_good') )
    self.assertEqual( KVL([ ( 'annotation2', None ) ]),
                      sections[1].find_entry('is_good').annotations )
    
    self.assertEqual( 'fruit', sections[2].header_.name )
    self.assertEqual( 'watermelon', sections[2].find_by_key('name') )
    self.assertEqual( 'false', sections[2].find_by_key('tart') )
    self.assertEqual( 'true', sections[2].find_by_key('is_good') )
    self.assertEqual( KVL([ ( 'annotation1', None ) ]),
                      sections[2].find_entry('is_good').annotations )
    
    self.assertEqual( 'fruit', sections[3].header_.name )
    self.assertEqual( 'strawberry', sections[3].find_by_key('name') )
    self.assertEqual( 'false', sections[3].find_by_key('tart') )
    self.assertEqual( 'true', sections[3].find_by_key('is_good') )
    self.assertEqual( None, sections[3].find_entry('is_good').annotations )

  def test_invalid_key(self):
    text = '''\
foo
  in.valid: bar
'''
    with self.assertRaises(simple_config.error) as ctx:
      simple_config.from_text(text)
      print(ctx)
    
  def test_add_section_explicit(self):
    c = simple_config()
    c.add_section('foo')

    c.add_section('fruit')
    c.find('fruit').set_value('name', 'kiwi')
    c.find('fruit').set_value('color', 'green')

    self.assertEqual( 'kiwi', c.find('fruit').get_value('name') )
    self.assertEqual( 'green', c.find('fruit').get_value('color') )
    
  def test_add_section_implicit(self):
    c = simple_config()
    c.find('fruit').set_value('name', 'kiwi')
    c.find('fruit').set_value('color', 'green')

    self.assertEqual( 'kiwi', c.find('fruit').get_value('name') )
    self.assertEqual( 'green', c.find('fruit').get_value('color') )
    
  def test_sections_names(self):
    text = '''\
fruit
  name: lemon

cheese
  name: brie

wine
  name: barolo
'''
    s = simple_config.from_text(text)
    self.assertEqual( [ 'fruit', 'cheese', 'wine' ], s.section_names() )
    self.assertTrue( s.sections_are_unique() )
    
  def test_sections_names_sections_with_same_names(self):
    text = '''\
fruit
  name: lemon
  flavor: tart

fruit
  name: apple
  flavor: sweet

fruit
  name: kiwi
  flavor: sweet
'''
    s = simple_config.from_text(text)
    self.assertEqual( [ 'fruit', 'fruit', 'fruit' ], s.section_names() )
    self.assertFalse( s.sections_are_unique() )

  def test_update_with_simple_config(self):
    text1 = '''\
fruit
  name: kiwi
  color: green
'''
    text2 = '''\
fruit
  name: lemon
  color: yellow
'''
    c1 = simple_config.from_text(text1)
    c2 = simple_config.from_text(text2)

    c1.update(c2)
    
    self.assertEqual( 'lemon', c1.fruit.name )
    self.assertEqual( 'yellow', c1.fruit.color )

    self.assertEqual( 'lemon', c2.fruit.name )
    self.assertEqual( 'yellow', c2.fruit.color )

  def test_update_with_dict(self):
    c = simple_config()
    c.fruit.name = 'kiwi'
    c.fruit.color = 'green'

    d = {
      'fruit': {
        'name': 'lemon',
        'color': 'yellow',
      },
    }
      
    c.update(d)
    
    self.assertEqual( 'lemon', c.fruit.name )
    self.assertEqual( 'yellow', c.fruit.color )

  def test_attributes(self):
    text = '''\
fruit
  name: lemon

cheese
  name: brie

wine
  name: barolo
'''
    s = simple_config.from_text(text)
    self.assertEqual( 'lemon', s.fruit.name )
    self.assertEqual( 'brie', s.cheese.name )
    self.assertEqual( 'barolo', s.wine.name )

    s.veggie.name = 'cauliflower'
    s.veggie.color = 'white'

    self.assertEqual( 'cauliflower', s.veggie.name )
    self.assertEqual( 'white', s.veggie.color )
    
  def test_to_dict(self):
    text = '''\
fruit
  name: lemon

cheese
  name: brie

wine
  name: barolo
'''
    s = simple_config.from_text(text)
    self.assertEqual( {
      'fruit': {
        'name': 'lemon',
      },
      'cheese': {
        'name': 'brie',
      },
      'wine': {
        'name': 'barolo',
      },
    }, s.to_dict() )

  def test_remove_section(self):
    text = '''\
fruit
  name: lemon

cheese
  name: brie

wine
  name: barolo
'''
    s = simple_config.from_text(text)
    s.remove_section('cheese')
    self.assertEqual( [ 'fruit', 'wine' ], s.section_names() )
    
  def test_replace_sections(self):
    text = '''\
fruit
  name: lemon

cheese1
  name: brie

cheese2
  name: cheddar

cheese3
  name: fontina

wine
  name: barolo
'''
    s = simple_config.from_text(text)

    old_section = s.section('cheese2')
    s.remove_section('cheese3')
    s.remove_section('cheese1')
    s.remove_section('cheese2')
    new_section = s.add_section('cheese')
    new_section.set_values(old_section.to_key_value_list())
    
    self.assertEqual( [ 'fruit', 'wine', 'cheese' ], s.section_names() )
    self.assertEqual( {
      'fruit': {
        'name': 'lemon',
      },
      'cheese': {
        'name': 'cheddar',
      },
      'wine': {
        'name': 'barolo',
      },
    }, s.to_dict() )
    
  def test_duplicate_key_get(self):
    text = '''\
fruit
  name: lemon
  flavor: tart
  color: yellow
  flavor: sweet
'''
    s = simple_config.from_text(text)

    self.assertEqual( 'sweet', s.fruit.flavor )

  def test_duplicate_key_set(self):
    text = '''\
fruit
  name: lemon
  flavor: tart
  color: yellow
  flavor: sweet
'''
    s = simple_config.from_text(text)

    s.fruit.flavor = 'rotten'
    
    expected = '''\
fruit
  name: lemon
  flavor: rotten
  color: yellow
  flavor: rotten
'''.strip()

    self.assertEqual( expected, str(s).strip() )
    
if __name__ == '__main__':
  unit_test.main()
