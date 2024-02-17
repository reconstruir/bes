#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from ..version.semantic_version import semantic_version
from ..common.tuple_util import tuple_util

class btl_lexer_desc_error(namedtuple('btl_lexer_desc_error', 'name, message')):
  
  def __new__(clazz, name, message):
    check.check_string(name)
    check.check_string(message)
    return clazz.__bases__[0].__new__(clazz, name, message)

  def to_dict(self):
    return dict(self._asdict())
  
  @classmethod
  def parse_node(clazz, n, source = '<unknown>'):
    check.check_node(n)
    check.check_string(source)

    return n.parse_key_value(source, result_class = btl_lexer_desc_error)

  @property
  def error_class_name(self):
    return f'{self.name}'
  
  def generate_code(self, buf):
    check.check_btl_code_gen_buffer(buf)

    code = f'''class {self.error_class_name}(btl_lexer_runtime_error):
  pass'''
    buf.write_lines(code)
    
  @classmethod
  def _check_cast_func(clazz, obj):
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
check.register_class(btl_lexer_desc_error, include_seq = False, cast_func = btl_lexer_desc_error._check_cast_func)
