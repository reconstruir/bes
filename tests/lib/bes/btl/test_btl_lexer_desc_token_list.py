#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.btl.btl_lexer_desc_token import btl_lexer_desc_token
from bes.btl.btl_lexer_desc_token_list import btl_lexer_desc_token_list
from bes.btl.btl_error import btl_error
from bes.testing.unit_test import unit_test

from _test_desc_mixin import _test_desc_mixin

class test_btl_lexer_desc_token_list(_test_desc_mixin, unit_test):

  def test_generate_code(self):
    tokens = btl_lexer_desc_token_list([
      btl_lexer_desc_token('kiwi', {}),
      btl_lexer_desc_token('lemon', {}),
      btl_lexer_desc_token('melon', {})
    ])
    token = btl_lexer_desc_token('kiwi', {})

    #s = self.call_buf_func(tokens, 'generate_code')
    #print(s)
    #return
    
    self.assert_code_equal('''class _token:

  KIWI = 'kiwi'
  LEMON = 'lemon'
  MELON = 'melon'
''', self.call_buf_func(tokens, 'generate_code') )
    
if __name__ == '__main__':
  unit_test.main()
