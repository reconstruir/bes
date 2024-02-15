#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.btl.btl_lexer_desc_error import btl_lexer_desc_error
from bes.btl.btl_lexer_desc_state_transition import btl_lexer_desc_state_transition
from bes.btl.btl_error import btl_error
from bes.testing.unit_test import unit_test

from _test_simple_lexer_mixin import _test_simple_lexer_mixin

class test_btl_lexer_desc_state(_test_simple_lexer_mixin, unit_test):

  def test_generate_code(self):
    error = btl_lexer_desc_error('e_bad', 'kiwi is bad')

    self.assert_python_code_text_equal('''\
class e_bad(btl_lexer_runtime_error):
  pass
''', self.call_function_with_buf(error, 'generate_code') )
  
if __name__ == '__main__':
  unit_test.main()
