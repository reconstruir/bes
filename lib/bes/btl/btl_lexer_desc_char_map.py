#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
import json
import pprint

from ..common.json_util import json_util
from ..system.check import check
from ..common.variable_manager import variable_manager

from .btl_error import btl_error
from .btl_lexer_desc_char import btl_lexer_desc_char

class btl_lexer_desc_char_map(object):
  
  def __init__(self, add_basic_chars = True):
    self._map = {}
    if add_basic_chars:
      for name, chars in self._BASIC_CHARS.items():
        desc_char = btl_lexer_desc_char(name, chars)
        self.add(desc_char)

  def __str__(self):
    return pprint.pformat(self._map)

  def __getitem__(self, char_name):
    return self._map[char_name]

  def __len__(self):
    len(self._map)
  
  def __contains__(self, char_name):
    return char_name in self._map

  def clone(self):
    result = btl_lexer_desc_char_map()
    result._map = copy.deepcopy(self._map)
    return result
  
  def to_dict(self, without_basic = True):
    result = {}
    for name, char in self._map.items():
      result[name] = char.to_dict()
    if without_basic:
      for name in self._BASIC_CHARS.keys():
        del result[name]
    return result

  def to_json(self):
    return json_util.to_json(self.to_dict(), indent = 2, sort_keys = False)
  
  def parse_union(self, chars):
    check.check_string(chars)

    parts = [ part.strip() for part in chars.split('|') ]
    parts = [ part for part in parts if part ]
    result = set()
    for part in parts:
      if part in self._map:
        cd = self._map[part]
        result = result | cd.chars
      else:
        if len(part) == 1 or part.startswith('${'):
          result.add(part)
        else:
          raise btl_error(f'Unknown char: "{part}"')
    return result

  def parse_and_add(self, name, chars):
    check.check_string(name)
    check.check_string(chars)

    parsed_chars = self.parse_union(chars)
    desc_char = btl_lexer_desc_char(name, parsed_chars)
    self.add(desc_char)

  def add(self, desc_char):
    check.check_btl_lexer_desc_char(desc_char)

    if desc_char.name in self._map:
      raise btl_error(f'Already in map: "{desc_char.name}"')
    self._map[desc_char.name] = desc_char

  @classmethod
  def from_json(clazz, text):
    check.check_string(text)

    result = btl_lexer_desc_char_map()
    d = json.loads(text)
    for name, char_dict in d.items():
      assert 'name' in char_dict
      assert 'chars' in char_dict
      name = char_dict['name']
      chars = char_dict['chars']
      chars_set = set(chars)
      desc_char = btl_lexer_desc_char(name, chars_set)
      result.add(desc_char)
    return result

  def substituted_variables(self, variables):
    check.check_variable_manager(variables)

    sub_map = {}
    for name, char in self._map.items():
      sub_map[name] = char.substituted_variables(variables)
    result = btl_lexer_desc_char_map(add_basic_chars = False)
    result._map = sub_map
    return result
      
  _BASIC_CHARS = {
    'c_alpha': set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'),
    'c_alpha_numeric': set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'),
    'c_amp': set('&'),
    'c_at': set('@'),
    'c_back_slash': set('\\'),
    'c_bang': set('!'),
    'c_caret': set('^'),
    'c_close_bracket': set(']'),
    'c_close_curly_bracket': set('}'),
    'c_close_parenthesis': set(')'),
    'c_colon': set(':'),
    'c_comma': set(','),
    'c_cr': set('\r'),
    'c_dollar': set('$'),
    'c_double_quote': set("\""),
    'c_eos': set('\0'),
    'c_equal': set('='),
    'c_grave_accent': set('`'),
    'c_greater_than': set('>'),
    'c_hash': set('#'),
    'c_less_than': set('<'),
    'c_lower_letter': set('abcdefghijklmnopqrstuvwxyz'),
    'c_minus': set('-'),
    'c_nl': set('\n'),
    'c_numeric': set('0123456789'),
    'c_open_bracket': set('['),
    'c_open_curly_bracket': set('{'),
    'c_open_parenthesis': set('('),
    'c_percent': set('%'),
    'c_period': set('.'),
    'c_pipe': set('|'),
    'c_plus': set('+'),
    'c_question_mark': set('?'),
    'c_semicolon': set(';'),
    'c_single_quote': set('\''),
    'c_slash': set('/'),
    'c_space': set(' '),
    'c_star': set('*'),
    'c_tab': set('\t'),
    'c_tilde': set('~'),
    'c_underscore': set('_'),
    'c_upper_letter': set('ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
    'c_ws': set(' \t'),
    'c_line_break': { '\r\n', '\n' },
    'c_punctuation': set('!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'),
  }
check.register_class(btl_lexer_desc_char_map)
