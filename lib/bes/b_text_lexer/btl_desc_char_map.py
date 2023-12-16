#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

from .btl_error import btl_error
from .btl_desc_char import btl_desc_char

class btl_desc_char_map(object):
  
  def __init__(self):
    self._map = {}
    for key, value in self._BASIC_CHARS.items():
      assert key not in self._map
      self._map[key] = btl_desc_char(key, value)

  def parse_union(self, s):
    check.check_string(s)
    
    parts = [ part.strip() for part in s.split('|') ]
    parts = [ part for part in parts if part ]
    result = set()
    for part in parts:
      if not part in self._map:
        raise btl_error(f'Unknown char: "{part}"')
      cd = self._map[part]
      result = result | cd.chars
    return result

  def __getitem__(self, key):
    return self._map[key]

  _BASIC_CHARS = {
    '&': '&',
    '_': '_',
    
    'c_amp': '&',
    'c_at': '@',
    'c_back_slash': '\\',
    'c_bang': '!',
    'c_caret': '^',
    'c_close_bracket': ']',
    'c_close_curly_bracket': '}',
    'c_close_parenthesis': ')',
    'c_colon': ':',
    'c_comma': ',',
    'c_cr': '\r',
    'c_dollar': '$',
    'c_double_quote': "\"",
    'c_eos': '\0',
    'c_equal': '=',
    'c_grave_accent': '`',
    'c_greater_than': '>',
    'c_hash': '#',
    'c_less_than': '<',
    'c_lower_letter': 'abcdefghijklmnopqrstuvwxyz',
    'c_minus': '-',
    'c_nl': '\n',
    'c_open_bracket': '[',
    'c_open_curly_bracket': '{',
    'c_open_parenthesis': '(',
    'c_percent': '%',
    'c_period': '.',
    'c_pipe': '|',
    'c_plus': '+',
    'c_question_mark': '?',
    'c_semicolon': ';',
    'c_single_quote': '\'',
    'c_slash': '/',
    'c_space': ' ',
    'c_star': '*',
    'c_tab': '\t',
    'c_white_space': ' \t',
    'c_tilde': '~',
    'c_underscore': '_',
    'c_upper_letter': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    'c_alpha_numeric': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
    'c_alpha': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
    'c_numeric': '0123456789',
}
check.register_class(btl_desc_char_map)
