#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check
from bes.common.type_checked_list import type_checked_list
from bes.key_value.key_value import key_value
from bes.key_value.key_value_list import key_value_list
from bes.text.string_list_parser import string_list_parser
from bes.compat.StringIO import StringIO

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

    parsed = [ p for p in string_list_parser.parse(text, options = string_list_parser.KEEP_QUOTES) ]
    if not parsed:
      raise ValueError('Invalid git attribute item.  Missing pattern: "{}"'.format(text))
    pattern = parsed.pop(0)
    attributes = key_value_list()
    for p in parsed:
      if '=' in p:
        attributes.extend(key_value_list.parse(p, key_value_list.KEEP_QUOTES))
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

class git_attributes_item_list(type_checked_list):

  __value_type__ = git_attributes_item
  
  def __init__(self, values = None):
    super(git_attributes_item_list, self).__init__(values = values)

  def sort_lexical(self, reverse = False):
    return self.sort(key = lambda item: item.pattern, reverse = reverse)
    
  def to_dict(self, short_hash = False):
    result = {}
    for item in self:
      if item.pattern in result:
        raise ValueError('duplicate pattern: "{}"'.format(item.pattern))
      result[item.pattern] = item
    return result

  def to_json(self, short_hash = False):
    d = self.to_dict(short_hash = short_hash)
    return json_util.to_json(d, indent = 2, sort_keys = True)
  
  def output(self, style, output_filename = None):
    git_output_style.check_style(style)

    with file_util.open_with_default(filename = output_filename) as fout:
      if style == 'brief':
        for tag in self:
          fout.write(tag.name)
          fout.write('\n')
      elif style == 'table':
        data = table(data = self._values)
        data.remove_column(3)
        data.remove_column(1)
        tt = text_table(data = data)
        tt.set_labels( ( 'TAG', 'COMMIT' ) )
        print(tt)
        pass
      elif style == 'json':
        fout.write(self.to_json(short_hash = True))
        fout.write('\n')
        
check.register_class(git_attributes_item_list, include_seq = False)
