#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.testing.unit_test import unit_test

from bes.bcli.bcli_parser_tree import bcli_parser_tree

class test_bcli_parser_tree(unit_test):

  def test_foo(self):
    t = bcli_parser_tree()
    t.set('fruit/kiwi', 'foo')
    n = t.get('fruit/kiwi')
    print(f'n={n}')
    
if __name__ == '__main__':
  unit_test.main()
