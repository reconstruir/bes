#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.config.ini.bc_ini_document import bc_ini_document

class test_bc_ini_document(unit_test):

  def test_get_section_value(self):
    text = '''
[fruit]
name=apple
color=red

[cheese]
name=vieux
smell=stink
'''
    doc = bc_ini_document(text)
    
    self.assertEqual( 'apple', doc.get_section_value('fruit', 'name') )
    self.assertEqual( 'red', doc.get_section_value('fruit', 'color') )

    self.assertEqual( 'vieux', doc.get_section_value('cheese', 'name') )
    self.assertEqual( 'stink', doc.get_section_value('cheese', 'smell') )

  def test_get_value(self):
    text = '''
name=grocery
version=1.0

[fruit]
name=apple
color=red

[cheese]
name=vieux
smell=stink
'''
    doc = bc_ini_document(text)

    self.assertEqual( 'grocery', doc.get_value('name') )
    self.assertEqual( '1.0', doc.get_value('version') )
    
if __name__ == '__main__':
  unit_test.main()
