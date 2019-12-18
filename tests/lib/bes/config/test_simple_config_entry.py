#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from bes.testing.unit_test import unit_test
from bes.config.simple_config_entry import simple_config_entry as SCE
from bes.config.simple_config_origin import simple_config_origin as SCO
from bes.key_value.key_value_list import key_value_list as KVL
from bes.key_value.key_value import key_value as KV

class test_simple_config_entry(unit_test):

  def test___str__(self):
    self.assertEqual( 'foo: bar', str(SCE(KV('foo', 'bar'), SCO('<unittest>', 1), None)) )
    self.assertEqual( 'foo[a=x,b=y]: bar', str(SCE(KV('foo', 'bar'), SCO('<unittest>', 1), KVL([ ( 'a', 'x' ), ( 'b', 'y' ) ]))) )
      
  def test_find_annotation(self):
    self.assertEqual( ( 'a', 'x' ),
                      SCE(KV('foo', 'bar'), SCO('<unittest>', 1), KVL([ ( 'a', 'x' ), ( 'b', 'y' ) ])).find_annotation('a') )
      
    self.assertEqual( None,
                      SCE(KV('foo', 'bar'), SCO('<unittest>', 1), KVL([ ( 'a', 'x' ), ( 'b', 'y' ) ])).find_annotation('notthere') )
      
  def test_has_annotation(self):
    self.assertEqual( True,
                      SCE(KV('foo', 'bar'), SCO('<unittest>', 1), KVL([ ( 'a', 'x' ), ( 'b', 'y' ) ])).has_annotation('a') )
      
    self.assertEqual( False,
                      SCE(KV('foo', 'bar'), SCO('<unittest>', 1), KVL([ ( 'a', 'x' ), ( 'b', 'y' ) ])).has_annotation('notthere') )
      
if __name__ == '__main__':
  unit_test.main()
