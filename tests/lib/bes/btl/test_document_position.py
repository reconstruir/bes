#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.btl.btl_document_position import btl_document_position

class test_btl_document_position(unit_test):

  def test___str__(self):
    self.assertEqual( '10,1', str(btl_document_position(10, 1)) )

  def test_moved(self):
    self.assertEqual( ( 11, 1 ), btl_document_position(10, 1).moved(1, 0) )
    
  def test_to_dict(self):
    self.assertEqual( {
      'line_number': 10,
      'column': 1,
    }, btl_document_position(10, 1).to_dict() )

  def test_parse_str(self):
    self.assertEqual( ( 10, 1 ), btl_document_position.parse_str('10,1') )

  def test_advanced(self):
    self.assertEqual( ( 10, 2 ), btl_document_position(10, 1).advanced('a') )
    self.assertEqual( ( 10, 3 ), btl_document_position(10, 1).advanced('aa') )
    self.assertEqual( ( 11, 1 ), btl_document_position(10, 1).advanced('\n') )
    self.assertEqual( ( 11, 1 ), btl_document_position(10, 1).advanced('\r\n') )

if __name__ == '__main__':
  unit_test.main()
