#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.btl.btl_lexer_desc_token import btl_lexer_desc_token
from bes.btl.btl_error import btl_error
from bes.testing.unit_test import unit_test
from bes.text.tree_text_parser import _text_node_data

from _test_lexer_desc_mixin import _test_lexer_desc_mixin

class test_btl_lexer_desc_token(_test_lexer_desc_mixin, unit_test):

  def test_generate_code_with_yield(self):
    token = btl_lexer_desc_token('kiwi', {})
    self.assert_code_equal( '''
KIWI = 'kiwi'
''', self.call_buf_func(token, 'generate_code') )

if __name__ == '__main__':
  unit_test.main()
