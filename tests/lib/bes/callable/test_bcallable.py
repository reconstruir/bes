#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.callable.bcallable import bcallable
from bes.testing.unit_test import unit_test

def _global_func(): pass
class test_bcallable(unit_test):

  def test_name_local_func(self):
    def _local_func(): pass
    self.assertEqual( f'{__name__}._local_func', bcallable.name(_local_func) )

  def test_name_global_func(self):
    self.assertEqual( f'{__name__}._global_func', bcallable.name(_global_func) )

  def test_name_lambda(self):
    f = lambda: 42
    self.assertEqual( f'{__name__}.<lambda>', bcallable.name(f) )

if __name__ == '__main__':
  unit_test.main()
