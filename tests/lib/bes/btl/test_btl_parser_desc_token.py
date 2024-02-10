#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.btl.btl_parser_desc_token import btl_parser_desc_token
from bes.btl.btl_error import btl_error
from bes.testing.unit_test import unit_test

from _test_simple_parser_mixin import _test_simple_parser_mixin

class test_btl_parser_desc_token(_test_simple_parser_mixin, unit_test):

  def test_generate_code_with_yield(self):
    token = btl_parser_desc_token('kiwi', {})
    self.assert_python_code_text_equal( '''
KIWI = 'kiwi'
''', self.call_function_with_buf(token, 'generate_code') )

if __name__ == '__main__':
  unit_test.main()
