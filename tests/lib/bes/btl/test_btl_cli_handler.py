#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.testing.unit_test import unit_test

from bes.btl.btl_cli_handler import btl_cli_handler

class test_btl_cli_handler(unit_test):

  def test__parse_code_filename(self):
    self.assertEqual(
      ( '_test', 'simple_lexer' ),
      btl_cli_handler._parse_code_filename('_test_simple_lexer.py')
    )

if __name__ == '__main__':
  unit_test.main()
