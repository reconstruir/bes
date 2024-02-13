#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.btl.btl_document_position import btl_document_position

class test_btl_document_position(unit_test):

  def test_move(self):
    self.assertEqual( ( 11, 1 ), btl_document_position(10, 1).moved(1, 0) )
    
if __name__ == '__main__':
  unit_test.main()
