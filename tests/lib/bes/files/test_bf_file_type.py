#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.files.bf_file_type import bf_file_type
from bes.testing.unit_test import unit_test

class test_bf_file_type(unit_test):
  
  def test_want_file(self):
    self.assertEqual( True, bf_file_type(bf_file_type.FILE).want_file )
    self.assertEqual( False, bf_file_type(bf_file_type.FILE).want_dir )
    self.assertEqual( False, bf_file_type(bf_file_type.FILE).want_link )
    self.assertEqual( False, bf_file_type(bf_file_type.FILE).want_device )
    self.assertEqual( False, bf_file_type(bf_file_type.FILE).want_socket )

  def test_want_dir(self):
    self.assertEqual( False, bf_file_type(bf_file_type.DIR).want_file )
    self.assertEqual( True, bf_file_type(bf_file_type.DIR).want_dir )
    self.assertEqual( False, bf_file_type(bf_file_type.DIR).want_link )
    self.assertEqual( False, bf_file_type(bf_file_type.DIR).want_device )
    self.assertEqual( False, bf_file_type(bf_file_type.DIR).want_socket )

  def test_want_link(self):
    self.assertEqual( False, bf_file_type(bf_file_type.LINK).want_file )
    self.assertEqual( False, bf_file_type(bf_file_type.LINK).want_dir )
    self.assertEqual( True, bf_file_type(bf_file_type.LINK).want_link )
    self.assertEqual( False, bf_file_type(bf_file_type.LINK).want_device )
    self.assertEqual( False, bf_file_type(bf_file_type.LINK).want_socket )
    
if __name__ == '__main__':
  unit_test.main()
