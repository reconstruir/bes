#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.testing.unit_test import unit_test
from bes.text.bindent import bindent

class test_bindent(unit_test):

  def test_indent_0(self):
    text = f'kiwi{os.linesep}orange{os.linesep}melon{os.linesep}'
    expected = f'kiwi{os.linesep}orange{os.linesep}melon{os.linesep}'
    self.assertEqual( expected, bindent.indent(text, 0) )

  def test_indent_1(self):
    text = f'kiwi{os.linesep}orange{os.linesep}melon{os.linesep}'
    expected = f' kiwi{os.linesep} orange{os.linesep} melon{os.linesep}'
    self.assertEqual( expected, bindent.indent(text, 1) )
    
  def test_indent_2(self):
    text = f'kiwi{os.linesep}orange{os.linesep}melon{os.linesep}'
    expected = f'  kiwi{os.linesep}  orange{os.linesep}  melon{os.linesep}'
    self.assertEqual( expected, bindent.indent(text, 2) )
    
  def test_indent_4(self):
    text = f'kiwi{os.linesep}orange{os.linesep}melon{os.linesep}'
    expected = f'    kiwi{os.linesep}    orange{os.linesep}    melon{os.linesep}'
    self.assertEqual( expected, bindent.indent(text, 4) )

  def test_indent_with_fix_empty_lines_true(self):
    text = f'kiwi{os.linesep}  {os.linesep}orange{os.linesep}'
    expected = f'__kiwi{os.linesep}{os.linesep}__orange{os.linesep}'
    self.assertEqual( expected, self._test(text, 2, True) )

  def test_indent_with_fix_empty_lines_false(self):
    text = f'kiwi{os.linesep}  {os.linesep}orange{os.linesep}'
    expected = f'__kiwi{os.linesep}____{os.linesep}__orange{os.linesep}'
    self.assertEqual( expected, self._test(text, 2, False) )

  def _test(self, text, indent_width, fix_empty_lines):
    result = bindent.indent(text, indent_width, fix_empty_lines = fix_empty_lines)
    return result.replace(' ', '_') #'\x25a1')
#\x20

if __name__ == '__main__':
  unit_test.main()
