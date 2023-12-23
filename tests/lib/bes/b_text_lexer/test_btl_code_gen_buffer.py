#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.b_text_lexer.btl_code_gen_buffer import btl_code_gen_buffer
from bes.testing.unit_test import unit_test

class test_btl_code_gen_buffer(unit_test):

  def test_get_value(self):
    b = btl_code_gen_buffer(indent_width = 2)
    b.write('kiwi')
    self.assertEqual( 'kiwi', b.get_value() )

  def test_get_value_with_eof_line_sep(self):
    b = btl_code_gen_buffer(indent_width = 2)
    b.write('kiwi')
    self.assertEqual( f'kiwi{os.linesep}', b.get_value(eof_line_sep = True) )

  def test_get_value_with_indent_width(self):
    b = btl_code_gen_buffer(indent_width = 2)
    b.write('kiwi')
    self.assertEqual( f'  kiwi', b.get_value(indent_width = 2) )
    
  def test_write_line(self):
    b = btl_code_gen_buffer(indent_width = 2)
    b.write_line('kiwi')
    b.write_line('lemon')
    self.assertEqual( f'kiwi{os.linesep}lemon{os.linesep}', b.get_value() )

  def test_push_indent(self):
    b = btl_code_gen_buffer(indent_width = 2)
    b.write_line('kiwi')
    b.push_indent()
    b.write_line('lemon')
    b.push_indent()
    b.write_line('melon')
    b.pop_indent()
    b.write_line('apple')
    self.assertEqual( f'kiwi{os.linesep}  lemon{os.linesep}    melon{os.linesep}  apple{os.linesep}', b.get_value() )

  def test_indent_pusher(self):
    b = btl_code_gen_buffer(indent_width = 2)
    b.write_line('kiwi')
    with b.indent_pusher() as c1:
      b.write_line('lemon')
      with b.indent_pusher() as c2:
        b.write_line('melon')
      b.write_line('apple')
    self.assertEqual( f'kiwi{os.linesep}  lemon{os.linesep}    melon{os.linesep}  apple{os.linesep}', b.get_value() )
  def test_write_lines(self):
    b = btl_code_gen_buffer(indent_width = 2)
    b.write_lines(f'kiwi{os.linesep}lemon{os.linesep}')
    self.assertEqual( f'kiwi{os.linesep}lemon{os.linesep}', b.get_value() )

  def test_write_lines_with_indent(self):
    b = btl_code_gen_buffer(indent_width = 2)
    with b.indent_pusher() as _:
      b.write_lines(f'kiwi{os.linesep}lemon{os.linesep}')
    self.assertEqual( f'  kiwi{os.linesep}  lemon{os.linesep}', b.get_value() )
    
if __name__ == '__main__':
  unit_test.main()
