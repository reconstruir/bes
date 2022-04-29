#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.hconfig.hconfig import hconfig
from bes.hconfig.hconfig_error import hconfig_error
from bes.hconfig.hconfig_caster_int import hconfig_caster_int

class test_hconfig(unit_test):

  def test_basic(self):
    d = {
      'timestamp': '666',
      'fruit': {
        'kiwi': { 'color': 'green', 'flavor': 'tart' },
        'apple': { 'color': 'red', 'flavor': 'sweet' },
        'lemon': { 'color': 'yellow', 'flavor': 'tart' },
      },
      'wine': {
        'barolo': { 'color': 'red', 'body': 'medium' },
        'bordeaux': { 'color': 'red', 'body': 'full' },
        'sancerre': { 'color': 'white', 'body': 'light' },
      },
    }
    c = hconfig(d)
    self.assertEqual( '666', c.timestamp )
    self.assertEqual( 'green', c.fruit.kiwi.color )
    with self.assertRaises(hconfig_error) as ctx:
      c.fruit.kiwi.price

  def test_register_caster(self):
    d = {
      'timestamp': '666',
      'fruit': {
        'kiwi': { 'color': 'green', 'flavor': 'tart' },
        'apple': { 'color': 'red', 'flavor': 'sweet' },
        'lemon': { 'color': 'yellow', 'flavor': 'tart' },
      },
      'wine': {
        'barolo': { 'color': 'red', 'body': 'medium' },
        'bordeaux': { 'color': 'red', 'body': 'full' },
        'sancerre': { 'color': 'white', 'body': 'light' },
      },
    }
    c = hconfig(d)
    c.register_caster('timestamp', hconfig_caster_int())
    self.assertEqual( 666, c.timestamp )
#    self.assertEqual( 'green', c.fruit.kiwi.color )
#    with self.assertRaises(hconfig_error) as ctx:
#      c.fruit.kiwi.price
      
if __name__ == '__main__':
  unit_test.main()
