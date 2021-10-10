#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check
from bes.compat.StringIO import StringIO
from bes.key_value.key_value import key_value
from bes.key_value.key_value_list import key_value_list
from bes.text.line_break import line_break
from bes.text.string_list_parser import string_list_parser
from bes.text.string_lexer_options import string_lexer_options

class git_attributes_item(namedtuple('git_attributes_item', 'pattern, attributes')):
  'A class to represent one .gitattributes file item'
  
  def __new__(clazz, pattern, attributes):
    check.check_string(pattern)
    check.check_key_value_list(attributes)
    
    return clazz.__bases__[0].__new__(clazz, pattern, attributes)

  def __str__(self):
    buf = StringIO()
    buf.write(self.pattern)
    for attr in self.attributes:
      buf.write(' ')
      if isinstance(attr.value, bool):
        if not attr.value:
          buf.write('-')
        buf.write(attr.key)
      else:
        buf.write(str(attr))
    return buf.getvalue()
  
  def to_dict(self):
    return dict(self._asdict())
  
  @classmethod
  def parse(clazz, text):
    check.check_string(text)

    parsed = [ p for p in string_list_parser.parse(text, options = string_lexer_options.KEEP_QUOTES) ]
    if not parsed:
      raise ValueError('Invalid git attribute item.  Missing pattern: "{}"'.format(text))
    pattern = parsed.pop(0)
    attributes = key_value_list()
    for p in parsed:
      if '=' in p:
        attributes.extend(key_value_list.parse(p, string_lexer_options.KEEP_QUOTES))
      else:
        attributes.append(clazz._parse_bool_attribute(p))
    return git_attributes_item(pattern, attributes)

  @classmethod
  def _parse_bool_attribute(clazz, text):
    if text.startswith('-'):
      name = text[1:]
      value = False
    else:
      name = text
      value = True
    return key_value(name, value)
  
check.register_class(git_attributes_item, include_seq = False)
