#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import collections
import re

from ..system.check import check

class variable(object):
  'Class to find an substitute shell style variabels in the forms $foo and ${foo}'

  AT_SIGN = 1 << 0
  BRACKET = 1 << 1
  DOLLAR_ONLY = 1 << 2
  PARENTHESIS = 1 << 3
  PERCENT = 1 << 4
  PERCENT_ONLY = 1 << 5

  ALL = AT_SIGN | BRACKET | DOLLAR_ONLY | PARENTHESIS | PERCENT | PERCENT_ONLY
  
  @classmethod
  def find_variables(clazz, s, patterns = None):
    check.check_string(s)
    check.check_int(patterns, allow_none = True)
    
    patterns = patterns or clazz.ALL
    expressions = clazz._mask_to_patterns(patterns)
    exp = ' | '.join(expressions)
    f = re.findall(exp, s, re.VERBOSE | re.DOTALL)
    result = set()
    for x in f:
      i = [ i for i in x if i ][0]
      result.add(i)
    return sorted(list(result))

  @classmethod
  def substitute(clazz, s, d, patterns = None):
    'Substitute vars in s with d.'
    check.check_dict(d, key_type = check.STRING_TYPES, value_type = ( str, collections.abc.Callable ))
    check.check_int(patterns, allow_none = True)

    patterns = patterns or clazz.ALL
    expressions = clazz._mask_to_patterns(patterns)

    if False:
#    if True:
      print(f's={s}')
      print(f'd={d}')
      print(f'patterns={patterns}')
      print(f'expressions={expressions}')
    
    exp = '|'.join(expressions)
    old_result = s
    new_result = None
    while True:
      new_result = clazz._substitute_exp(old_result, d, exp)
      if new_result == old_result:
        break
      old_result = new_result
    return new_result

  @classmethod
  def _substitute_exp(clazz, s, d, exp):
    def _replace(match):
      whole_match = match.group()
      variable_name = clazz._first_valid_group(match.groups())
      result = d.get(variable_name, whole_match)
      if callable(result):
        result = result()
      return str(result)
    return re.sub(exp, _replace, s)
    
  @classmethod
  def _first_valid_group(clazz, groups):
    for g in groups:
      if g:
        return g
    return None

  @classmethod
  def has_rogue_dollar_signs(clazz, s):
    'Return True of the string has rogue unescaped dollar signs.'
    return bool(re.search(r'(?<!\\)\$', s))

  _PATTERNS = [
    ( BRACKET, r'(?<!\\)\$\{([A-Za-z_][A-Za-z0-9_]*)\}' ),
    ( PARENTHESIS, r'(?<!\\)\$\(([A-Za-z_][A-Za-z0-9_]*)\)' ),
    ( DOLLAR_ONLY, r'(?<!\\)\$([A-Za-z_][A-Za-z0-9_]*)' ),
    ( PERCENT, r'(?<!\\)\%([A-Za-z_][A-Za-z0-9_]*)\%' ),
    ( PERCENT_ONLY, r'(?<!\\)\%([A-Za-z_][A-Za-z0-9_]*)' ),
    ( AT_SIGN, r'(?<!\\)\@([A-Za-z_][A-Za-z0-9_]*)\@' ),
  ]
  
  @classmethod
  def _mask_to_patterns(clazz, mask):
    result = []
    for key, value in clazz._PATTERNS:
      if (mask & key) != 0:
        result.append(value)
    return result

  @classmethod
  def is_single_variable(clazz, s, patterns = None):
    check.check_string(s)
    check.check_int(patterns, allow_none = True)

    patterns = patterns or clazz.ALL
    expressions = clazz._mask_to_patterns(patterns)
    exp = ' | '.join(expressions)
    return re.match(exp, s, re.VERBOSE | re.DOTALL) != None

  @classmethod
  def single_variable_name(clazz, s, patterns = None):
    check.check_string(s)
    check.check_int(patterns, allow_none = True)

    v = clazz.find_variables(s, patterns = patterns)
    if v and len(v) == 1:
      return v[0]
    return None
