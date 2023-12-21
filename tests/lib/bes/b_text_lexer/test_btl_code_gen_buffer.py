#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.b_text_lexer.btl_code_gen_buffer import btl_code_gen_buffer
from bes.testing.unit_test import unit_test

class test_btl_code_gen_buffer(unit_test):

  def test_get_value_eof_line_sep_true(self):
    b = btl_code_gen_buffer(indent_width = 2)
    b.write_line(f'if x == y:')
    b.write_line(f'  print("true")')
    b.write_line(f'else:')
    b.write(f'  print("false")')
    self.assertEqual('''\
if x == y:
  print("true")
else:
  print("false")
''', b.get_value(eof_line_sep = True) )
    
  def test_get_value_eof_line_sep_false(self):
    b = btl_code_gen_buffer(indent_width = 2)
    b.write_line(f'if x == y:')
    b.write_line(f'  print("true")')
    b.write_line(f'else:')
    b.write(f'  print("false")')
    self.assertEqual('''\
if x == y:
  print("true")
else:
  print("false")''', b.get_value(eof_line_sep = False) )
    
if __name__ == '__main__':
  unit_test.main()
