#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

class btl_desc_variable_base(object):
  
  def __init__(self, name, default_value):
    check.check_string(name)
    check.check_string(default_value)

    self._name = name
    self._default_value = default_value

  @property
  def name(self):
    return self._name

  @property
  def default_value(self):
    return self._default_value
  
  def to_dict(self):
    return {
      'name': self.name,
      'default_value': self.default_value,
    }

  def to_tuple(self):
    return ( self.name, self.default_value )
  
  @classmethod
  def parse_node(clazz, n, source = '<unknown>'):
    check.check_node(n)
    check.check_string(source)
    
    name, default_value = clazz._parse_key_value(n.data.text, delimiter = ':')
    return clazz(name, default_value)
  
  def generate_code(self, buf, errors):
    check.check_btl_code_gen_buffer(buf)

    assert False, f'Not Implemented'

  @classmethod
  def _parse_key_value(clazz, s, delimiter = '='):
    key, delim, default_value = s.partition(delimiter)
    assert delim.strip() == delimiter
    return ( key.strip(), default_value.strip() )
