#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.fs.testing.temp_content import temp_content
from bes.refactor.refactor_ast import refactor_ast
from bes.refactor.refactor_options import refactor_options
from bes.testing.unit_test import unit_test

class test_refactor_ast(unit_test):

  @classmethod
  def _make_temp_content(clazz, items):
    return temp_content.write_items_to_temp_dir(items, delete = not clazz.DEBUG)

  def test_grep(self):
    kiwi_py = r'''
class kiwi(object):
  def foo(self):
    return 1

  def bar(self):
    return 2
'''
    lemon_py = r'''
from .kiwi import kiwi
class lemon(kiwi):
  def foo(self):
    return 1

  def bar(self):
    return 2
'''

    orange_py = r'''
class orange(kiwi):
  def foo(self):
    return 1

  def bar(self):
    return 2

  def foo2(self):
    return 3

  def foo_prime(self):
    return 3

  def foo_caca(self, *kargs, **kwargs):
    return 3

  def foo_caca2(self, a, b, sweet = True):
    return 3

  def foo_caca3(self, *kargs):
    return 3

  def foo_caca4(self, **kwargs):
    return 3

  def foo_caca5(self, a, b,
                c, d):
    return 3
'''
    
    tmp_dir = self._make_temp_content([
      temp_content('file', 'fruit/lemon.py', f'{lemon_py}', 0o0644),
      temp_content('file', 'fruit/kiwi.py', f'{kiwi_py}', 0o0644),
      temp_content('file', 'orange.py', f'{orange_py}', 0o0644),
    ])
    r = refactor_ast.grep([ tmp_dir ], 'foo', 'function')
    for item in r:
      print(f'{item.filename}:')
      print(f'{item.line_number}: {item.snippet}')
      continue
      print(f'   posonlyargs: {item.node.args.posonlyargs}')
      print(f'          args: {[ arg.arg for arg in item.node.args.args ]}')
      print(f'        vararg: {item.node.args.vararg}')
      print(f'    kwonlyargs: {item.node.args.kwonlyargs}')
      print(f'   kw_defaults: {item.node.args.kw_defaults}')
      print(f'         kwarg: {item.node.args.kwarg}')
      print(f'      defaults: {[ c.value for c in item.node.args.defaults ]}')
      print('')

# arg = (identifier arg, expr? annotation, string? type_comment)
#           attributes (int lineno, int col_offset, int? end_lineno, int? end_col_offset)
      
if __name__ == '__main__':
  unit_test.main()
