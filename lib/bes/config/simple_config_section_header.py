#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.common.string_util import string_util
from bes.text.line_numbers import line_numbers
from bes.common.tuple_util import tuple_util
from bes.compat.StringIO import StringIO

from collections import namedtuple

from .simple_config_error import simple_config_error
from .simple_config_origin import simple_config_origin

class simple_config_section_header(namedtuple('simple_config_section_header', 'name, extends, origin, extra_text')):

  def __new__(clazz, name, extends = None, origin = None, extra_text = None):
    check.check_string(name)
    check.check_string(extends, allow_none = True)
    check.check_simple_config_origin(origin, allow_none = True)
    check.check_string(extra_text, allow_none = True)
    
    return clazz.__bases__[0].__new__(clazz, name, extends, origin, extra_text)

  def __str__(self):
    buf = StringIO()
    buf.write(self.name)
    if self.extends:
      buf.write(' extends ')
      buf.write(self.extends)
    if self.extra_text:
      buf.write(' ')
      buf.write(self.extra_text)
    return buf.getvalue()
  
  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)
  
  @classmethod
  def parse_text(clazz, text, origin):
    parts = string_util.split_by_white_space(text, strip = True)
    if len(parts) == 0:
      raise simple_config_error('Invalid config section header: "{}"'.format(text), origin)
    name = parts.pop(0)
    extends = None
    extra_text = None
    if len(parts) > 0:
      if parts[0] == 'extends':
        if len(parts) < 2:
          numbered_text = line_numbers.add_line_numbers(text)
          msg = 'extends directive missing parent: "{}"'.format(numbered_text)
          raise simple_config_error(msg, origin)
        parts.pop(0)
        extends = parts.pop(0)

    if len(parts) > 0:
      extra_text = ' '.join(parts)
    return simple_config_section_header(name, extends = extends, origin = origin, extra_text = extra_text)
  
check.register_class(simple_config_section_header)
