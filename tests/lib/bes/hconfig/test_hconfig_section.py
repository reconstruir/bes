#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.hconfig.hconfig_section import hconfig_section
from bes.hconfig.hconfig import hconfig
from bes.hconfig.hconfig_error import hconfig_error
from bes.system.check import check

class test_hconfig_section(unit_test):

  def test_basic(self):
    fruit = {
      'kiwi': { 'color': 'green', 'flavor': 'tart' },
      'apple': { 'color': 'red', 'flavor': 'sweet' },
      'lemon': { 'color': 'yellow', 'flavor': 'tart' },
    }
    s = hconfig_section(fruit, hconfig({}), None)
    self.assertEqual( 'green', s.kiwi.color )

  def test_to_dict(self):
    fruit = {
      'kiwi': { 'color': 'green', 'flavor': 'tart' },
      'apple': { 'color': 'red', 'flavor': 'sweet' },
      'lemon': { 'color': 'yellow', 'flavor': 'tart' },
    }
    s = hconfig_section(fruit, hconfig({}), None)
    self.assertEqual( {
      'apple': { 'color': 'red', 'flavor': 'sweet' },
      'kiwi': { 'color': 'green', 'flavor': 'tart' },
      'lemon': { 'color': 'yellow', 'flavor': 'tart' },
    }, s.to_dict() )
    
if __name__ == '__main__':
  unit_test.main()
