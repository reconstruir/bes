#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
from .string_util import string_util
from .check import check

class variable(object):
  'Class to find an substitute shell style variabels in the forms $foo, ${foo}, $(foo) and @FOO@'

  DOLLAR_ONLY = 0x01
  PARENTHESIS = 0x02
  BRACKET = 0x04
  AT_SIGN = 0x08
  ALL = DOLLAR_ONLY | PARENTHESIS | BRACKET | AT_SIGN
  
  DOLLAR_ONLY_PATTERN = re.compile('\$[\w_][\w\n_]*')
  DOLLAR_PARENTHESIS_PATTERN = re.compile('\$\([\w_][\w\n_]*\)')
  DOLLAR_BRACKET_PATTERN = re.compile('\$\{[\w_][\w\n_]*\}')
  AT_SIGN_PATTERN = re.compile('\@[\w_][\w\n_]*@')

  KEY_FORMATS = {
    DOLLAR_ONLY_PATTERN: '$%s',
    DOLLAR_PARENTHESIS_PATTERN: '$(%s)',
    DOLLAR_BRACKET_PATTERN: '${%s}',
    AT_SIGN_PATTERN: '@%s@',
  }

  @classmethod
  def _mask_to_patterns(clazz, mask):
    result = []
    if (mask & clazz.DOLLAR_ONLY) != 0:
      result.append(clazz.DOLLAR_ONLY_PATTERN)
    if (mask & clazz.PARENTHESIS) != 0:
      result.append(clazz.DOLLAR_PARENTHESIS_PATTERN)
    if (mask & clazz.BRACKET) != 0:
      result.append(clazz.DOLLAR_BRACKET_PATTERN)
    if (mask & clazz.AT_SIGN) != 0:
      result.append(clazz.AT_SIGN_PATTERN)
    return result
  
  @classmethod
  def find_variables(clazz, s, patterns = ALL):
    'Return a list of variables found in s.'
    result = []
    for pattern in clazz._mask_to_patterns(patterns):
      found = pattern.findall(s)
      names = [ clazz._var_to_name(v, pattern) for v in found ]
      result.extend(names)
    return sorted(list(set(result)))

  @classmethod
  def substitute(clazz, s, d, word_boundary = True, patterns = ALL):
    'Substitute vars in s with d.'
    check.check_dict(d, key_type = check.STRING_TYPES, value_type = check.STRING_TYPES)
    replacements = {}
    for key, value in d.items():
      check.check_string(key)
      check.check_string(value)
      for pattern in clazz._mask_to_patterns(patterns):
        formatted_key = clazz.KEY_FORMATS[pattern] % (key)
        replacements[formatted_key] = value
    old_result = s
    new_result = None
    while True:
      new_result = string_util.replace(old_result, replacements, word_boundary = word_boundary)
      changed = new_result != old_result
      if not changed:
        break
      old_result = new_result
    return new_result

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
