#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from __future__ import unicode_literals

import os.path as path
from bes.testing.unit_test import unit_test
from bes.config.simple_config import simple_config
from bes.config.simple_config_options import simple_config_options
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
      s.find_all_sections('foo')

    sections = s.find_all_sections('credential')
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
    self.assertTrue( s.has_unique_section('credential') )
    self.assertFalse( s.has_unique_section('nothere') )

  def test_wildcard(self):
    text = '''\
common
  test: false
  name: Artur

release-*
  test: true
  port: 5502
'''

    s = simple_config.from_text(text)

    import re
    matcher = lambda section, pattern: re.search(section.header_.name, pattern)

    self.assertTrue( s.has_unique_section('release-1v.5166', matcher = matcher) )
    self.assertTrue( s.has_unique_section('common', matcher = matcher) )

    self.assertFalse( s.has_unique_section('commo-n', matcher = matcher) )
    self.assertFalse( s.has_unique_section('releas-e', matcher = matcher) )

    sections = s.find_all_sections('release-1v.5166', matcher = matcher)
    self.assertEqual( 1, len(sections) )
    self.assertEqual( {'test': 'true', 'port': '5502'}, sections[0].to_dict() )

    sections = s.find_all_sections('common', matcher = matcher)
    self.assertEqual( 1, len(sections) )
    self.assertEqual( {'test': 'false', 'name': 'Artur'}, sections[0].to_dict() )
    
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

      sections = s.find_all_sections('credential')
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
    sections = s.find_all_sections('credential')
    self.assertEqual( 1, len(sections) )
    with self.assertRaises(simple_config.error) as context:
      sections[0].to_dict(resolve_env_vars = True)

  def test_extends(self):
    text = '''\
fruit
  name: apple
  color: red
  base: fructose

cheese
  name: brie
  type: creamy

kiwi extends fruit
  color: green
  where: new zealand
'''
    
    s = simple_config.from_text(text)

    sections = s.find_all_sections('kiwi')
    self.assertEqual( 1, len(sections) )
    self.assertEqual( 'kiwi', sections[0].header_.name )
    self.assertEqual( 'fruit', sections[0].header_.extends )
    self.assertEqual( 'green', sections[0].find_by_key('color') )
    self.assertEqual( 'apple', sections[0].find_by_key('name') )
    self.assertEqual( 'fructose', sections[0].find_by_key('base') )

    self.assertEqual( {
      'base': 'fructose',
      'color': 'green',
      'name': 'apple',
      'where': 'new zealand',
    }, sections[0].to_dict() )

    self.assertEqual( KVL([
      ( 'name', 'apple'),
      ( 'color', 'red'),
      ( 'base', 'fructose'),
      ( 'color', 'green'),
      ( 'where', 'new zealand'),
    ]), sections[0].to_key_value_list() )
    
    self.assertEqual( True, sections[0].has_key('base') )
    self.assertEqual( True, sections[0].has_key('color') )
    self.assertEqual( True, sections[0].has_key('name') )

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
      s.find_all_sections('foo')

    sections = s.find_all_sections('fruit')
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
  in@valid: bar
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

  def test_delete_value(self):
    c = simple_config()
    c.add_section('fruit')
    s = c.find('fruit')
    s.set_value('name', 'kiwi')
    s.set_value('color', 'green')
    self.assertEqual( {
      'color': 'green',
      'name': 'kiwi',
    }, s.to_dict() )

    s.delete_value('name')
    self.assertEqual( {
      'color': 'green',
    }, s.to_dict() )

  def test_sections_names(self):
    text = '''\
fruit
  name: lemon

cheese
  name: brie

wine
  name: barolo

release-*
  bane: arma
'''
    s = simple_config.from_text(text)
    self.assertEqual( [ 'fruit', 'cheese', 'wine', 'release-*' ], s.section_names() )
    self.assertTrue( s.sections_are_unique() )
    self.assertTrue( s.has_section('fruit') )
    self.assertTrue( s.has_section('wine') )
    self.assertFalse( s.has_section('liquor') )
    
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
    
  def test_find_key(self):
    text = '''\
fruit
  name: lemon
  flavor: tart
  color: yellow
  flavor: sweet
'''
    s = simple_config.from_text(text)

    section = s.section('fruit')

    self.assertEqual( 'lemon', section.find_by_key('name') )

    with self.assertRaises(simple_config.error):
      self.assertEqual( None, section.find_by_key('notthere') )
    
  def test_match_key(self):
    text = '''\
fruit
  name: lemon
  flavor: tart
  color: yellow
  flavor: sweet
'''
    s = simple_config.from_text(text)

    section = s.section('fruit')

    self.assertEqual( 'lemon', section.match_by_key('name') )
    self.assertEqual( 'sweet', section.match_by_key('fl*') )
    self.assertEqual( 'sweet', section.match_by_key('*') )
    self.assertEqual( 'lemon', section.match_by_key('n???') )

    with self.assertRaises(simple_config.error):
      self.assertEqual( None, section.match_by_key('notthere') )

  def test_section_extra_text(self):
    text = '''\
kiwi foo
  color: green
  flavor: tart
'''
    s = simple_config.from_text(text)
    self.assertEqual( 'green', s.kiwi.color )
    self.assertEqual( 'tart', s.kiwi.flavor )

    section = s.section('kiwi')
    self.assertEqual( 'kiwi', section.header_.name )
    self.assertEqual( 'foo', section.header_.extra_text )
      
  def test_section_extends_extra_text(self):
    text = '''\
fruit
  name:fruit

kiwi extends fruit foo
  color: green
  flavor: tart
'''
    s = simple_config.from_text(text)
    self.assertEqual( 'green', s.kiwi.color )
    self.assertEqual( 'tart', s.kiwi.flavor )

    section = s.section('kiwi')
    self.assertEqual( 'kiwi', section.header_.name )
    self.assertEqual( 'fruit', section.header_.extends )
    self.assertEqual( 'foo', section.header_.extra_text )

  @classmethod
  def _parse_ssh_config_entry(clazz, text, origin, options):
    from bes.system.check import check
    from bes.common.string_util import string_util
    from bes.key_value.key_value import key_value
    from bes.config.simple_config_entry import simple_config_entry

    check.check_string(text)
    check.check_simple_config_origin(origin)
    check.check_simple_config_options(options)
    
    hints = {}
    if '=' in text:
      kv = key_value.parse(text)
      hints['delimiter'] = '='
    else:
      parts = string_util.split_by_white_space(text, strip = True)
      if len(parts) < 2:
        raise simple_config_error('invalid sss config entry (not enough parts): "{}"'.format(text), origin)
      kv = key_value(parts.pop(0), ' '.join(parts))
      hints['delimiter'] = ' '
    return simple_config_entry(kv, origin = origin, hints = hints)

  @classmethod
  def _ssh_config_entry_formatter(clazz, entry, key_column_width = None):
    assert 'delimiter' in entry.hints
    return entry.value.to_string(delimiter = entry.hints['delimiter'])
    
  def test_custom_ssh_config_parser(self):
    text = '''
Host kiwi
  User fred
  IdentityFile ~/.ssh/id_rsa
  IdentitiesOnly yes

Host lemon
  User fred
  IdentityFile ~/.ssh/id_rsa

Host apple
  User fred
  IdentityFile ~/.ssh/id_rsa
  Hostname 172.16.1.1
  Port 666

Host *
  IPQoS=throughput
'''
    c = simple_config.from_text(text,
                                entry_parser = self._parse_ssh_config_entry,
                                entry_formatter = self._ssh_config_entry_formatter)
    self.assert_string_equal( text, str(c), strip = True, native_line_breaks = True )
      
  def test_multi_line_values(self):
    text = '''
kiwi
  key: -----BEGIN RSA PRIVATE KEY-----
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
       -----END RSA PRIVATE KEY-----
'''
    c = simple_config.from_text(text)

    key_expected = '''\
-----BEGIN RSA PRIVATE KEY-----
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12
-----END RSA PRIVATE KEY-----'''
    
    self.assert_string_equal( key_expected, c.kiwi.key, native_line_breaks = True )

  def test_clear_value(self):
    text = '''\
fruit
  name: lemon
  flavor: tart
  color: yellow
  flavor: sweet
'''
    s = simple_config.from_text(text)

    section = s.section('fruit')
    section.clear_values()
    
    expected = '''\
fruit

'''
    self.assertEqual( expected, str(s) )

  def test_get_all_values(self):
    text = '''\
fruit
  name: lemon
  flavor: tart
  color: yellow
  flavor: sweet
'''
    s = simple_config.from_text(text)
    self.assertEqual( [ 'tart', 'sweet' ], s.fruit.get_all_values('flavor') )
    
  def test_get_all_values_with_dups(self):
    text = '''\
fruit
  name: lemon
  flavor: tart
  color: yellow
  flavor: sweet
  flavor: tart
'''
    s = simple_config.from_text(text)
    self.assertEqual( [ 'tart', 'sweet', 'tart' ], s.fruit.get_all_values('flavor') )

  def test_get_all_values_with_extends(self):
    text = '''\
fruit
  base: fructose
  arg: yummy=1
  arg: tart=0

kiwi extends fruit
  arg: tart=1
  arg: color=green
  arg: where="new zealand"
'''
    s = simple_config.from_text(text)
    self.assertEqual( [ 'yummy=1', 'tart=0' ], s.fruit.get_all_values('arg') )
    self.assertEqual( [ 'yummy=1', 'tart=0', 'tart=1', 'color=green', 'where="new zealand"' ], s.kiwi.get_all_values('arg') )

  def test_sections_with_key_value(self):
    text = '''\
s1
  color: red

s2
  color: green

s3
  color: red

s4
  color: blue

s5
  taste: tart
'''
    s = simple_config.from_text(text)
    self.assertEqual( [ 's1', 's3' ],  s.sections_with_key_value('color', 'red') )
    self.assertEqual( [ 's2' ],  s.sections_with_key_value('color', 'green') )
    self.assertEqual( [],  s.sections_with_key_value('cheese', 'blue') )

  def test_clone(self):
    text = '''\
fruit
  name: lemon
  flavor: tart
  color: yellow

wine
  name: barolo
  flavor: good
  color: red

cheese
  name: brie
  flavor: nice
  color: cream
'''
    s1 = simple_config.from_text(text)
    self.assert_string_equal( text, str(s1), native_line_breaks = True )

    s2 = s1.clone()
    self.assert_string_equal( text, str(s2), native_line_breaks = True )

    s2.remove_section('wine')
    self.assert_string_equal( text, str(s1), native_line_breaks = True )
    self.assertNotEqual( text, str(s2) )

    s2.cheese.add_value('price', '100')
    self.assert_string_equal( text, str(s1), native_line_breaks = True )
    self.assertNotEqual( text, str(s2) )

  def xtest_unicode(self):
    c = simple_config()
    section = c.add_section('s1')
    section.add_value('v1', u'this Д is cyrillic')

    self.assertEqual( u'''\
s1
  v1: this Д is cyrillic
''', str(c) )

  def test_set_value(self):
    text = '''\
fruit
  name: lemon
  flavor: tart
  color: yellow
'''
    s = simple_config.from_text(text)
    self.assertEqual( 'tart', s.get_value('fruit', 'flavor') )
    s.set_value('fruit', 'flavor', 'sweet')
    self.assertEqual( 'sweet', s.get_value('fruit', 'flavor') )
    
  def test_set_values(self):
    text = '''\
fruit
  name: lemon
  flavor: tart
  color: yellow
'''
    s = simple_config.from_text(text)
    self.assertEqual( {
      'name': 'lemon',
      'flavor': 'tart',
      'color': 'yellow'
    }, s.get_values('fruit') )
    s.set_values('fruit', {
      'name': 'kiwi',
      'color': 'green',
      'where': 'new zealand',
    })
    self.assertEqual( {
      'name': 'kiwi',
      'flavor': 'tart',
      'color': 'green',
      'where': 'new zealand',
    }, s.get_values('fruit') )

  def test_set_value_new_section(self):
    text = '''\
fruit
  name: lemon
  flavor: tart
  color: yellow
'''
    s = simple_config.from_text(text)
    s.set_value('cheese', 'name', 'brie')
    s.set_value('cheese', 'texture', 'creamy')
    self.assertEqual( 'brie', s.get_value('cheese', 'name') )
    self.assertEqual( 'creamy', s.get_value('cheese', 'texture') )

    expected = '''\
fruit
  name: lemon
  flavor: tart
  color: yellow

cheese
  name: brie
  texture: creamy
'''
    self.assert_string_equal( expected, str(s), strip = True, native_line_breaks = True, multi_line = True )

  def test_empty_content(self):
    s = simple_config(source = '<unit_test>')
    s.set_values('cheese', { 'name': 'brie', 'texture': 'creamy' })
    expected = '''\
cheese
  name: brie
  texture: creamy
'''

    self.assert_string_equal( expected, str(s), strip = True, native_line_breaks = True, multi_line = True )
    
  def test_empty_content(self):
    s = simple_config.from_text('')
    self.assertEqual( [], s.section_names() )

  def test_dots_in_keys(self):
    text = '''\
foo
  kiwi_3.8: a
  kiwi_3.9: b

bar
  kiwi_3.8: c
  kiwi_3.9: d
'''
    options = simple_config_options(key_check_type = simple_config_options.KEY_CHECK_ANY)
    s = simple_config.from_text(text, options = options)
    self.assertEqual( 'a', s.get_value('foo', 'kiwi_3.8') )
    self.assertEqual( 'b', s.get_value('foo', 'kiwi_3.9') )
    self.assertEqual( 'c', s.get_value('bar', 'kiwi_3.8') )
    self.assertEqual( 'd', s.get_value('bar', 'kiwi_3.9') )
    
  def test_variables_section(self):
    text = '''\
kiwi
  color: ${COLOR}
  flavor: ${FLAVOR}
  size: small

apple
  color: ${COLOR}
  flavor: ${FLAVOR}
  size: small

lemon
  color: ${COLOR}
  flavor: ${FLAVOR}
  size: small
'''
    tmp = self.make_temp_file(content = text, suffix = '.config')
    s = simple_config.from_file(tmp)
    s.kiwi.set_variables({
      'COLOR': 'green',
      'FLAVOR': 'tart',
    })
    s.apple.set_variables({
      'COLOR': 'red',
      'FLAVOR': 'sweet',
    })
    self.assertEqual( 'small', s.kiwi.size )
    self.assertEqual( 'green', s.kiwi.color )
    self.assertEqual( 'tart', s.kiwi.flavor )

    self.assertEqual( 'small', s.apple.size )
    self.assertEqual( 'red', s.apple.color )
    self.assertEqual( 'sweet', s.apple.flavor )

    self.assertEqual( 'small', s.lemon.size )
    with self.assertRaises(simple_config.error):
      s.lemon.color
    with self.assertRaises(simple_config.error):
      s.lemon.flavor

  def test_variables_global(self):
    text = '''\
kiwi
  color: ${COLOR}
  flavor: ${FLAVOR}
  size: small

apple
  color: ${COLOR}
  flavor: ${FLAVOR}
  size: small

lemon
  color: ${COLOR}
  flavor: ${FLAVOR}
  size: small
'''
    tmp = self.make_temp_file(content = text, suffix = '.config')
    s = simple_config.from_file(tmp)
    s.set_variables({
      'COLOR': 'green',
      'FLAVOR': 'tart',
    })
    self.assertEqual( 'small', s.kiwi.size )
    self.assertEqual( 'green', s.kiwi.color )
    self.assertEqual( 'tart', s.kiwi.flavor )

    self.assertEqual( 'small', s.apple.size )
    self.assertEqual( 'green', s.apple.color )
    self.assertEqual( 'tart', s.apple.flavor )

    self.assertEqual( 'small', s.lemon.size )
    self.assertEqual( 'green', s.lemon.color )
    self.assertEqual( 'tart', s.lemon.flavor )

  def test_variables_global_and_section(self):
    text = '''\
kiwi
  color: ${COLOR}
  flavor: ${FLAVOR}
  size: small

apple
  color: ${COLOR}
  flavor: ${FLAVOR}
  size: small

lemon
  color: ${COLOR}
  flavor: ${FLAVOR}
  size: small
'''
    tmp = self.make_temp_file(content = text, suffix = '.config')
    s = simple_config.from_file(tmp)
    s.set_variables({
      'COLOR': 'green',
      'FLAVOR': 'tart',
    })
    s.apple.set_variables({
      'COLOR': 'red',
      'FLAVOR': 'sweet',
    })
    self.assertEqual( 'small', s.kiwi.size )
    self.assertEqual( 'green', s.kiwi.color )
    self.assertEqual( 'tart', s.kiwi.flavor )

    self.assertEqual( 'small', s.apple.size )
    self.assertEqual( 'red', s.apple.color )
    self.assertEqual( 'sweet', s.apple.flavor )

    self.assertEqual( 'small', s.lemon.size )
    self.assertEqual( 'green', s.lemon.color )
    self.assertEqual( 'tart', s.lemon.flavor )
    
if __name__ == '__main__':
  unit_test.main()
