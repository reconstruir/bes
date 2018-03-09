#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.address import address as A

class test_address(unit_test):

  def test_parse_city_and_state(self):
    pass #self.assertEqual( ( 'Foo', 'CA', comments.strip_line('Foo, CA') )
  #self.assertEqual( 'foo', comments.strip_line('foo#comment') )
    
  def test_state_is_valid(self):
    self.assertTrue( A.state_is_valid('CA') )
    self.assertTrue( A.state_is_valid('ca') )
    self.assertFalse( A.state_is_valid(' ca') )

    self.assertFalse( A.state_is_valid('NOTTHERE') )
    self.assertFalse( A.state_is_valid('notthere') )
    self.assertFalse( A.state_is_valid(' notthere') )
    
if __name__ == '__main__':
  unit_test.main()
