#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.common.string_util import string_util

from collections import namedtuple

from .simple_config_error import simple_config_error
from .simple_config_origin import simple_config_origin

class simple_config_section_header(namedtuple('simple_config_section_header', 'name, extends, origin')):

  def __new__(clazz, name, extends, origin):
    check.check_string(name)
    check.check_string(extends, allow_none = True)
    check.check_simple_config_origin(origin)
    return clazz.__bases__[0].__new__(clazz, name, extends, origin)

  @classmethod
  def parse_text(clazz, text, origin):
    parts = string_util.split_by_white_space(text, strip = True)
    num_parts = len(parts)
    if num_parts == 1:
      return simple_config_section_header(parts[0], None, origin)
    elif num_parts == 3:
      name = parts[0]
      extends_directive = parts[1]
      extends_name = parts[2]
      if extends_directive != 'extends':
        raise simple_config_error('Invalid config section directive: "{}"'.format(extends_directive, origin))
      return simple_config_section_header(name, extends_name, origin)
    else:
      raise simple_config_error('Invalid config section header: "{}"'.format(text), origin)
  
check.register_class(simple_config_section_header)
