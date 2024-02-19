#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.config.ini.bc_ini_document import bc_ini_document

class test_bc_ini_document(unit_test):

  def test_foo(self):
    text = '''
[fruit]
name=apple
color=red

[cheese]
name=vieux
smell=stink
'''
    doc = bc_ini_document(text) 
    
if __name__ == '__main__':
  unit_test.main()
