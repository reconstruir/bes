#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.hconfig.hconfig import hconfig

class test_hconfig(unit_test):

  def test_basic(self):
    d = {
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
    
if __name__ == '__main__':
  unit_test.main()
