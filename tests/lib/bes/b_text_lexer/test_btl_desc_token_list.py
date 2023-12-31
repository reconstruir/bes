#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.b_text_lexer.btl_desc_token import btl_desc_token
from bes.b_text_lexer.btl_desc_token_list import btl_desc_token_list
from bes.b_text_lexer.btl_error import btl_error
from bes.testing.unit_test import unit_test

from keyval_desc_mixin import keyval_desc_mixin

class test_btl_desc_token_list(keyval_desc_mixin, unit_test):

  def test_generate_code(self):
    tokens = btl_desc_token_list([
      btl_desc_token('kiwi'),
      btl_desc_token('lemon'),
      btl_desc_token('melon')
    ])
    token = btl_desc_token('kiwi')

    #s = self.call_buf_func(tokens, 'generate_code', '_fruit', 'kiwi')
    #print(s)
    #return
    
    self.assert_code_equal('''class _fruit_kiwi_lexer_token:

  KIWI = 'kiwi'
  LEMON = 'lemon'
  MELON = 'melon'
''', self.call_buf_func(tokens, 'generate_code', '_fruit', 'kiwi') )
    
if __name__ == '__main__':
  unit_test.main()
