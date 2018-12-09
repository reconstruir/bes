#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json
from bes.system import compat
from bes.compat import StringIO
from bes.common import check, string_util, type_checked_list, variable

from .string_list_parser import string_list_parser
from .string_lexer import string_lexer_options

class string_list(type_checked_list, string_lexer_options.CONSTANTS):

  __value_type__ = compat.STRING_TYPES
  
  def __init__(self, values = None):
    super(string_list, self).__init__(values = values)
    
  def to_string(self, delimiter = ';', quote = False):
    buf = StringIO()
    first = True
    for s in self._values:
      if not first:
        buf.write(delimiter)
      first = False
      if quote:
        s = string_util.quote_if_needed(s)
      buf.write(s)
    return buf.getvalue()
    
  def __str__(self):
    return self.to_string()

  @classmethod
  def parse(clazz, text, options = 0):
    result = string_list()
    for s in string_list_parser.parse(text, options = options):
      result.append(s)
    return result

  def quote(self):
    self._values = [ string_util.quote(s) for s in self._values ]
  
  def unquote(self):
    self._values = [ string_util.unquote(s) for s in self._values ]
  
  def strip(self):
    self._values = [ s.strip() for s in self._values ]
  
  def remove_empties(self):
    self._values = [ s for s in self._values if s ]

  def substitute_variables(self, d, word_boundary = True):
    self._values = [ variable.substitute(s, d, word_boundary = word_boundary) for s in self._values ]

  def to_json(self, indent = 2):
    return json.dumps(self._values, indent = indent)

  @classmethod
  def from_json(clazz, text):
    return string_list(json.loads(text))
    
check.register_class(string_list, include_seq = False)
