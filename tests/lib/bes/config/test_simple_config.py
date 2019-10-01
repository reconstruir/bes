#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from bes.testing.unit_test import unit_test
from bes.config.simple_config import simple_config as SC
from bes.system.env_override import env_override

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
    self.assertEqual( 'download', sections[0].find_by_key('type') )
    self.assertEqual( 'upload', sections[1].find_by_key('type') )
    self.assertEqual( {
      'provider': 'pcloud',
      'type': 'download',
      'email': 'email1@bar.com',
      'password': 'sekret1',
      }, sections[0].to_dict() )
    
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
      
if __name__ == '__main__':
  unit_test.main()
