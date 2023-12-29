#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.b_text_lexer.btl_desc_token import btl_desc_token
from bes.b_text_lexer.btl_desc_token_list import btl_desc_token_list
from bes.b_text_lexer.btl_error import btl_error
from bes.testing.unit_test import unit_test

from keyval_desc_mixin import keyval_desc_mixin

class test_btl_desc_token_list(keyval_desc_mixin, unit_test):

  def test__make_token_class_code(self):
    tokens = btl_desc_token_list([
      btl_desc_token('kiwi'),
      btl_desc_token('lemon'),
      btl_desc_token('melon')
    ])
    token = btl_desc_token('kiwi')
    self.assert_code_equal('''
class _fruit_kiwi_lexer_token(object):

  def __init__(self, lexer):
    check.check_text_lexer(lexer)
  
    self._lexer = lexer
  
  KIWI = 'kiwi'
  def make_kiwi(self, value, position):
    return lexer_token(self.KIWI, value, self._lexer.position)
  
  LEMON = 'lemon'
  def make_lemon(self, value, position):
    return lexer_token(self.LEMON, value, self._lexer.position)
  
  MELON = 'melon'
  def make_melon(self, value, position):
    return lexer_token(self.MELON, value, self._lexer.position)
''', self.call_buf_func(tokens, 'generate_code', '_fruit', 'kiwi') )
    
if __name__ == '__main__':
  unit_test.main()
