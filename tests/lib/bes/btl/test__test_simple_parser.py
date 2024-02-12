#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.system.host import host
from bes.system.check import check
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

from bes.btl.btl_parser_base import btl_parser_base
from bes.btl.btl_parser_state_base import btl_parser_state_base
from bes.btl.btl_parser_tester_mixin import btl_parser_tester_mixin
from bes.btl.btl_parser_runtime_error import btl_parser_runtime_error

from _test_simple_lexer import _test_simple_lexer
from _test_simple_parser import _test_simple_parser
  
class test_btl_parser_base(btl_parser_tester_mixin, unit_test):

  def test_parse(self):
    l = _test_simple_lexer()
    p = _test_simple_parser(l)
    text = '''
fruit=apple
color=red

fruit=kiwi
color=green
'''
    result = p.parse(text)
    self.assert_python_code_text_equal( '''
n_root;
  n_key_value;
    n_key;t_key:fruit:p=1,2:i=1
    n_value;t_value:apple:p=7,2:i=3
  n_key_value;
    n_key;t_key:color:p=1,3:i=5
    n_value;t_value:red:p=7,3:i=7
  n_key_value;
    n_key;t_key:fruit:p=1,5:i=10
    n_value;t_value:kiwi:p=7,5:i=12
  n_key_value;
    n_key;t_key:color:p=1,6:i=14
    n_value;t_value:green:p=7,6:i=16
''', str(result.root_node) )
    
if __name__ == '__main__':
  unit_test.main()
