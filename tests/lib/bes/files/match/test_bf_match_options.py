#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.files.match.bf_match_options import bf_match_options

from bes.testing.unit_test import unit_test

class test_bf_match_options(unit_test):
  
  def test___init__(self):
    options = bf_match_options()
                                     
if __name__ == '__main__':
  unit_test.main()
