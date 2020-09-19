#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.compat.StringIO import StringIO
from bes.key_value.key_value import key_value
from bes.key_value.key_value_list import key_value_list
from bes.text.line_break import line_break

from collections import namedtuple

class simple_config_entry(namedtuple('simple_config_entry', 'value, origin, annotations, hints')):

  def __new__(clazz, value, origin = None, annotations = None, hints = None):
    check.check_key_value(value)
    check.check_simple_config_origin(origin, allow_none = True)
    check.check_key_value_list(annotations, allow_none = True)
    check.check_dict(hints, allow_none = True)
    
    return clazz.__bases__[0].__new__(clazz, value, origin, annotations, hints)
    
  def __str__(self):
    return self.to_string()

  def to_string(self, sort = False):
    buf_left = StringIO()
    buf_left.write(self.value.key)
    if self.annotations:
      buf_left.write('[')
      for i, annotation in enumerate(self.annotations):
        if i != 0:
          buf_left.write(',')
        buf_left.write(annotation.key)
        if annotation.value:
          buf_left.write('=')
          buf_left.write(annotation.value)
      buf_left.write(']')
    buf_left.write(': ')
    left_side = buf_left.getvalue()
    buf_right = StringIO()
    buf_right.write(left_side)
    value_lines = self.value.value.split(line_break.DEFAULT_LINE_BREAK)
    value_lines = value_lines if not sort else sorted(value_lines)
    indent = ' ' * (len(left_side) + 2)
    for i, line in enumerate(value_lines):
      if i > 0:
        buf_right.write(line_break.DEFAULT_LINE_BREAK)
        buf_right.write(indent)
      buf_right.write(line)
    return buf_right.getvalue()

  def has_annotation(self, annotation_key):
    check.check_string(annotation_key)
    return self.find_annotation(annotation_key) is not None

  def find_annotation(self, annotation_key):
    check.check_string(annotation_key)
    if not self.annotations:
      return None
    return self.annotations.find_by_key(annotation_key)
  
check.register_class(simple_config_entry)
