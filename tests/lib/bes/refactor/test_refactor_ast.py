#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import os
import os.path as path

from bes.fs.testing.temp_content import temp_content
from bes.refactor.refactor_ast import refactor_ast
from bes.refactor.refactor_options import refactor_options
from bes.testing.unit_test import unit_test
from bes.fs.file_util import file_util
from bes.common.json_util import json_util

class test_refactor_ast(unit_test):

  def test_grep(self):
    t = self._test_grep([
      temp_content('file', 'fruit/lemon.py', f'{self._LEMON_PY}', 0o0644),
      temp_content('file', 'fruit/kiwi.py', f'{self._KIWI_PY}', 0o0644),
      temp_content('file', 'orange.py', f'{self._ORANGE_PY}', 0o0644),
    ], 'foo', 'function', word_boundary = True)
    self.assert_string_equal_fuzzy(r'''
[
  [
    "fruit/kiwi.py",
    "  def foo(self):\n    return 1",
    [
      [
        3,
        "  def foo(self):"
      ],
      [
        4,
        "    return 1"
      ]
    ]
  ],
  [
    "fruit/lemon.py",
    "  def foo(self):\n    return 1",
    [
      [
        4,
        "  def foo(self):"
      ],
      [
        5,
        "    return 1"
      ]
    ]
  ],
  [
    "orange.py",
    "  def foo(self):\n    return 1",
    [
      [
        3,
        "  def foo(self):"
      ],
      [
        4,
        "    return 1"
      ]
    ]
  ]
]
''', t.json )

  def test_function_add_arg(self):
    tmp_dir = self._make_temp_content([
      temp_content('file', 'fruit/lemon.py', f'{self._LEMON_PY}', 0o0644),
      temp_content('file', 'fruit/kiwi.py', f'{self._KIWI_PY}', 0o0644),
      temp_content('file', 'orange.py', f'{self._ORANGE_PY}', 0o0644),
    ])
    options = refactor_options(word_boundary = True)
    refactor_ast.function_add_arg([ tmp_dir ], 'foo', 'added_arg', options = options)
    self.assert_text_file_equal_fuzzy('''\
from .kiwi import kiwi
class lemon(kiwi):
  def foo(self, added_arg):
    return 1

  def bar(self):
    return 2
''', f'{tmp_dir}/fruit/lemon.py' )

    self.assert_text_file_equal_fuzzy('''\
class kiwi(object):
  def foo(self, added_arg):
    return 1

  def bar(self):
    return 2
''', f'{tmp_dir}/fruit/kiwi.py' )

    self.assert_text_file_equal_fuzzy('''\
class orange(kiwi):
  def foo(self, added_arg):
    return 1

  def bar(self):
    return 2

  def foo2(self):
    return 3

  def foo_prime(self):
    return 3

  def foo_test(self, *kargs, **kwargs):
    return 3

  def foo_test2(self, a, b, sweet = True):
    return 3

  def foo_test3(self, *kargs):
    return 3

  def foo_test4(self, **kwargs):
    return 3

  def foo_test5(self, a, b,
                c, d):
    return 3
''', f'{tmp_dir}/orange.py' )
    
  _KIWI_PY = r'''
class kiwi(object):
  def foo(self):
    return 1

  def bar(self):
    return 2
'''
  _LEMON_PY = r'''
from .kiwi import kiwi
class lemon(kiwi):
  def foo(self):
    return 1

  def bar(self):
    return 2
'''

  _ORANGE_PY = r'''
class orange(kiwi):
  def foo(self):
    return 1

  def bar(self):
    return 2

  def foo2(self):
    return 3

  def foo_prime(self):
    return 3

  def foo_test(self, *kargs, **kwargs):
    return 3

  def foo_test2(self, a, b, sweet = True):
    return 3

  def foo_test3(self, *kargs):
    return 3

  def foo_test4(self, **kwargs):
    return 3

  def foo_test5(self, a, b,
                c, d):
    return 3
'''

  _test_grep_result = namedtuple('_test_grep_result', 'tmp_dir, result, json')
  def _test_grep(self, content, text, node_type, word_boundary = False):
    tmp_dir = self._make_temp_content(content)
    options = refactor_options(word_boundary = word_boundary)
    real_result = refactor_ast.grep([ tmp_dir ], text, node_type, options = options)
    result = []
    for item in real_result:
      filename = file_util.remove_head(item.filename, tmp_dir + os.sep)
      t = ( filename, item.snippet, item.snippet_lines )
      result.append(t)
    json = json_util.to_json(result, indent = 2)
    return self._test_grep_result(tmp_dir, real_result, json)
  
  @classmethod
  def _make_temp_content(clazz, items):
    return temp_content.write_items_to_temp_dir(items, delete = not clazz.DEBUG)
  
if __name__ == '__main__':
  unit_test.main()
