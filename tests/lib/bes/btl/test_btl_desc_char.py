#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.btl.btl_desc_char import btl_desc_char
from bes.testing.unit_test import unit_test

class test_test_btl_desc_char(unit_test):

  def test_as_dict_from_string(self):
    self.assertEqual( {
      'name': 'kiwi',
      'chars': { 65 },
      }, btl_desc_char('kiwi', 'A').as_dict )
    self.assertEqual( {
      'name': 'kiwi',
      'chars': { 65, 66 },
      }, btl_desc_char('kiwi', 'AB').as_dict )

  def test_as_dict_from_int(self):
    self.assertEqual( {
      'name': 'kiwi',
      'chars': { 65 },
      }, btl_desc_char('kiwi', 65).as_dict )

  def test_as_dict_from_int(self):
    self.assertEqual( {
      'name': 'kiwi',
      'chars': { 65 },
      }, btl_desc_char('kiwi', 65).as_dict )

  def test_as_dict_from_int_list(self):
    self.assertEqual( {
      'name': 'kiwi',
      'chars': { 65 },
      }, btl_desc_char('kiwi', [ 65 ]).as_dict )
    self.assertEqual( {
      'name': 'kiwi',
      'chars': { 65, 66 },
      }, btl_desc_char('kiwi', [ 65, 66 ]).as_dict )

  def test_as_dict_from_int_set(self):
    self.assertEqual( {
      'name': 'kiwi',
      'chars': { 65 },
      }, btl_desc_char('kiwi', { 65 }).as_dict )
    self.assertEqual( {
      'name': 'kiwi',
      'chars': { 65, 66 },
      }, btl_desc_char('kiwi', { 65, 66 }).as_dict )
    
if __name__ == '__main__':
  unit_test.main()
