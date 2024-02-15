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

from bes.config.ini.bc_ini_lexer import bc_ini_lexer
from bes.config.ini.bc_ini_parser import bc_ini_parser

from _test_ini_mixin import _test_ini_mixin

class test_bc_ini_parser(btl_parser_tester_mixin, _test_ini_mixin, unit_test):

  def test_parse_empty(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    result = p.parse('')
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
  n_sections;
''', str(result.root_node) )

  def test_parse_global_comment_only(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    result = p.parse(';empty')
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
  n_sections;
''', str(result.root_node) )

  def test_parse_section_comment_only(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    result = p.parse('''[fruit]
;empty''')
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
  n_sections;
    n_section;t_section_name:fruit:p=1,2:i=1
''', str(result.root_node) )
    
  def test_parse_global_only(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    text = '''
fruit=apple
color=red

fruit=kiwi
color=green
'''
    result = p.parse(text)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
    n_key_value;
      n_key;t_key:fruit:p=2,1:i=1
      n_value;t_value:apple:p=2,7:i=3
    n_key_value;
      n_key;t_key:color:p=3,1:i=5
      n_value;t_value:red:p=3,7:i=7
    n_key_value;
      n_key;t_key:fruit:p=5,1:i=10
      n_value;t_value:kiwi:p=5,7:i=12
    n_key_value;
      n_key;t_key:color:p=6,1:i=14
      n_value;t_value:green:p=6,7:i=16
  n_sections;    
''', str(result.root_node) )

  def test_parse_one_empty_section(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    result = p.parse('[fruit]')
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
  n_sections;
    n_section;t_section_name:fruit:p=1,2:i=1
''', str(result.root_node) )

  def test_parse_two_empty_sections(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    result = p.parse('[fruit]\n[cheese]\n')
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
  n_sections;
    n_section;t_section_name:fruit:p=1,2:i=1
    n_section;t_section_name:cheese:p=2,2:i=5
''', str(result.root_node) )
    
  def test_parse_one_section(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    text = '''
[fruit]
name=apple
color=red
'''
    result = p.parse(text)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
  n_sections;
    n_section;t_section_name:fruit:p=2,2:i=2
      n_key_value;
        n_key;t_key:name:p=3,1:i=5
        n_value;t_value:apple:p=3,6:i=7
      n_key_value;
        n_key;t_key:color:p=4,1:i=9
        n_value;t_value:red:p=4,7:i=11
''', str(result.root_node) )

  def test_parse_two_sections(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    text = '''
[fruit]
name=apple
color=red

[cheese]
name=vieux
smell=stink
'''
    result = p.parse(text)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
  n_sections;
    n_section;t_section_name:fruit:p=2,2:i=2
      n_key_value;
        n_key;t_key:name:p=3,1:i=5
        n_value;t_value:apple:p=3,6:i=7
      n_key_value;
        n_key;t_key:color:p=4,1:i=9
        n_value;t_value:red:p=4,7:i=11
    n_section;t_section_name:cheese:p=6,2:i=15
      n_key_value;
        n_key;t_key:name:p=7,1:i=18
        n_value;t_value:vieux:p=7,6:i=20
      n_key_value;
        n_key;t_key:smell:p=8,1:i=22
        n_value;t_value:stink:p=8,7:i=24
''', str(result.root_node) )

  def test_parse_multiple_sessions(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    text = '''
fruit=apple
color=red
'''
    result = p.parse(text)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
    n_key_value;
      n_key;t_key:fruit:p=2,1:i=1
      n_value;t_value:apple:p=2,7:i=3
    n_key_value;
      n_key;t_key:color:p=3,1:i=5
      n_value;t_value:red:p=3,7:i=7
  n_sections;    
''', str(result.root_node) )

    text = '''
fruit=melon
color=green
'''
    result = p.parse(text)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
    n_key_value;
      n_key;t_key:fruit:p=2,1:i=1
      n_value;t_value:melon:p=2,7:i=3
    n_key_value;
      n_key;t_key:color:p=3,1:i=5
      n_value;t_value:green:p=3,7:i=7
  n_sections;    
''', str(result.root_node) )

  def test_parse_section_key_only_ends_in_line_break(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    text = '''
[fruit]
name=
'''
    result = p.parse(text)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
  n_sections;
    n_section;t_section_name:fruit:p=2,2:i=2
      n_key_value;
        n_key;t_key:name:p=3,1:i=5
        n_value;t_value::p=3,6
''', str(result.root_node) )

  def test_parse_section_key_only_ends_in_eos(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    text = '''
[fruit]
name='''
    result = p.parse(text)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
  n_sections;
    n_section;t_section_name:fruit:p=2,2:i=2
      n_key_value;
        n_key;t_key:name:p=3,1:i=5
        n_value;t_value::p=3,6
''', str(result.root_node) )

  def test_parse_global_key_only_ends_in_line_break(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    text = '''
name=
'''
    result = p.parse(text)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
    n_key_value;
      n_key;t_key:name:p=2,1:i=1
      n_value;t_value::p=2,6
  n_sections;    
''', str(result.root_node) )

  def test_parse_global_key_only_ends_in_eos(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    text = '''
name='''
    result = p.parse(text)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
    n_key_value;
      n_key;t_key:name:p=2,1:i=1
      n_value;t_value::p=2,6
  n_sections;    
''', str(result.root_node) )

  def test_parse_command_instead_of_value(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    text = '''
kiwi = ; foo    
'''
    result = p.parse(text)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
    n_key_value;
      n_key;t_key:kiwi:p=2,1:i=1
      n_value;t_value::p=2,7
  n_sections;
''', str(result.root_node) )
    
  def xtest_caca(self):
    source = self.caca_filename('test_data/gitea.app.ini')
    text = self.caca_text('test_data/gitea.app.ini')
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    result = p.parse(text, source = source)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
''', str(result.root_node) )
    
if __name__ == '__main__':
  unit_test.main()
