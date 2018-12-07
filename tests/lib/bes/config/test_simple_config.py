#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.config import simple_config as SC

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

    sections = s.find_sections('foo')
    self.assertEqual( [], sections )

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
    
if __name__ == '__main__':
  unit_test.main()
