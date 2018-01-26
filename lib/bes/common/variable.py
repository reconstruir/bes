#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
from .string_util import string_util
from .check import check

class variable(object):
  'variable'

  DOLLAR_ONLY_PATTERN = re.compile('\$[\w_][\w\n_]*')
  DOLLAR_PARENTHESIS_PATTERN = re.compile('\$\([\w_][\w\n_]*\)')
  DOLLAR_BRACKET_PATTERN = re.compile('\$\{[\w_][\w\n_]*\}')
  AT_SIGN_PATTERN = re.compile('\@[\w_][\w\n_]*@')

  VARIABLE_PATTERNS = [
    DOLLAR_ONLY_PATTERN,
    DOLLAR_PARENTHESIS_PATTERN,
    DOLLAR_BRACKET_PATTERN,
    AT_SIGN_PATTERN,
  ]
  
  KEY_FORMATS = {
    DOLLAR_ONLY_PATTERN: '$%s',
    DOLLAR_PARENTHESIS_PATTERN: '$(%s)',
    DOLLAR_BRACKET_PATTERN: '${%s}',
    AT_SIGN_PATTERN: '@%s@',
  }

  @classmethod
  def find_variables(clazz, s):
    'Return a list of variables found in s.'
    result = []
    for pattern in clazz.VARIABLE_PATTERNS:
      found = pattern.findall(s)
      names = [ clazz._var_to_name(v, pattern) for v in found ]
      result.extend(names)
    return sorted(list(set(result)))

  @classmethod
  def substitute(clazz, s, d):
    'Substitute vars in s with d.'
    replacements = {}
    for key, value in d.items():
      check.check_string(key)
      check.check_string(value)
      for pattern in clazz.VARIABLE_PATTERNS:
        formatted_key = clazz.KEY_FORMATS[pattern] % (key)
        replacements[formatted_key] = value
    return string_util.replace(s, replacements, word_boundary = True)

  @classmethod
  def has_rogue_dollar_signs(clazz, s):
    'Return True of the string has rogue unescaped dollar signs.'
    s = s.replace('\\$', '')
    return '$' in s
  
  @classmethod
  def _var_to_name(clazz, var, pattern):
    'Convert a dollar sign variable into just the name.  $foo/${foo}/$(foo) => foo'
    if pattern == clazz.DOLLAR_ONLY_PATTERN:
      assert len(var) >= 2
      assert var[0] == '$'
      return var[1:]
    elif pattern in [ clazz.DOLLAR_PARENTHESIS_PATTERN, clazz.DOLLAR_BRACKET_PATTERN ]:
      assert len(var) >= 4
      assert var[0] == '$'
      return var[2:-1]
    elif pattern == clazz.AT_SIGN_PATTERN:
      assert len(var) >= 3
      assert var[0] == '@'
      assert var[-1] == '@'
      return var[1:-1]
    else:
      raise RuntimeError('Unknown pattern: %s' % (pattern))
