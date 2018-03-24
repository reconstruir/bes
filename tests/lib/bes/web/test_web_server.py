#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.address import address as A

class test_web_server(unit_test):

  def test_basic(self):
    self.assertEqual( ( 'Foo Bar', 'CA' ), A.parse_city_and_state('Foo Bar, CA') )
    self.assertEqual( ( 'Foo Bar', 'CA' ), A.parse_city_and_state('CA, Foo Bar') )
    self.assertEqual( ( 'Foo Bar', 'CA' ), A.parse_city_and_state('Foo Bar CA') )
    self.assertEqual( ( 'Foo Bar', 'CA' ), A.parse_city_and_state('CA Foo Bar') )
    self.assertEqual( ( 'Foo-Bar', 'CA' ), A.parse_city_and_state('Foo-Bar, CA') )
    self.assertEqual( ( 'Foo-Bar', 'CA' ), A.parse_city_and_state('CA, Foo-Bar') )
    self.assertEqual( None, A.parse_city_and_state('IRACK, Baddad') )
    
  def test_state_is_valid(self):
    self.assertTrue( A.state_is_valid('CA') )
    self.assertTrue( A.state_is_valid('ca') )
    self.assertFalse( A.state_is_valid(' ca') )

    self.assertFalse( A.state_is_valid('NOTTHERE') )
    self.assertFalse( A.state_is_valid('notthere') )
    self.assertFalse( A.state_is_valid(' notthere') )
    
if __name__ == '__main__':
  unit_test.main()
