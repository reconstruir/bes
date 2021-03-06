#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.compat import StringIO
from bes.common import check, object_util, string_util, type_checked_list, variable
from bes.text import string_lexer_options

from .key_value_parser import key_value_parser
from .key_value import key_value

class key_value_list(type_checked_list, string_lexer_options.CONSTANTS):

  __value_type__ = key_value
  
  def __init__(self, values = None):
    super(key_value_list, self).__init__(values = values)

  @classmethod
  def cast_value(clazz, entry):
    if isinstance(entry, tuple):
      return key_value(*entry)
    return entry

  def __contains__(self, v):
    if check.is_string(v):
      return self.contains_key(v)
    return super(key_value_list, self).__contains__(v)
  
  def contains_key(self, key):
    for v in self._values:
      if v.key == key:
        return True
    return False
  
  def to_string(self, delimiter = '=', value_delimiter = ';', quote = False):
    buf = StringIO()
    first = True
    for kv in iter(self):
      if not first:
        buf.write(value_delimiter)
      first = False
      buf.write(kv.to_string(delimiter = delimiter, quote_value = quote))
    return buf.getvalue()
    
  def __str__(self):
    return self.to_string()

  def find_key_value(self, kv):
    check.check_key_value(kv)
    for next_kv in self._values:
      if next_kv == kv:
        return next_kv
    return None

  def find_by_key(self, key):
    for next_kv in self._values:
      if next_kv.key == key:
        return next_kv
    return None

  def find_by_last_key(self, key):
    for next_kv in reversed(self._values):
      if next_kv.key == key:
        return next_kv
    return None

  def find_all_key(self, key):
    result = []
    for next_kv in self._values:
      if next_kv.key == key:
        result.append(next_kv)
    return result

  def remove_key(self, key):
    self._values = [ kv for kv in self._values if kv.key != key ]

  @classmethod
  def parse(clazz, text, options = 0, delimiter = '=', empty_value = None, log_tag = None):
    check.check_string(text)
    result = clazz()
    for kv in key_value_parser.parse(text, options = options, delimiter = delimiter,
                                     empty_value = empty_value, log_tag = log_tag):
      result.append(kv)
    return result

  def is_homogeneous(self, key_type, value_type):
    'Return True if all items in d are of the given key_type and value_type.'
    for kv in self._values:
      if not kv.is_instance(key_type, value_type):
        return False
    return True

  def to_dict(self):
    result = {}
    for next_kv in self._values:
      result[next_kv.key] = next_kv.value
    return result

  @classmethod
  def from_dict(clazz, d):
    check.check_dict(d)
    result = clazz()
    for key, value in sorted(d.items()):
      check.check_string(key)
      result.append(key_value(key, value))
    return result

  def quote_strings(self):
    for i, kv in enumerate(self._values):
      if string_util.is_string(kv.value):
        self._values[i] = key_value(kv.key, string_util.quote(kv.value))
  
  def unquote_strings(self):
    for i, kv in enumerate(self._values):
      if string_util.is_string(kv.value):
        self._values[i] = key_value(kv.key, string_util.unquote(kv.value))

  def substitute_variables(self, d, word_boundary = True):
    for i, kv in enumerate(self._values):
      self._values[i] = key_value(kv.key, variable.substitute(kv.value, d, word_boundary = word_boundary))

  def replace(self, key, new_kv):
    check.check_string(key)
    check.check_key_value(new_kv)
    for i, next_kv in enumerate(self._values):
      if next_kv.key == key:
        self._values[i] = new_kv
      
  def all_keys(self):
    return [ kv.key for kv in self ]
      
  def all_values(self):
    return [ kv.value for kv in self ]
      
check.register_class(key_value_list, include_seq = False)
